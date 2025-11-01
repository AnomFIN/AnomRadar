"""
Command-line interface for AnomRadar v2.

Uses Typer for CLI commands and Rich for beautiful output.
Includes global exception handling and crash protection.
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from anomradar import __version__
from anomradar.core.config import get_config
from anomradar.core.logging import setup_logging, get_logger, get_console
from anomradar.core.cache import Cache
from anomradar.scanners.http import HttpScanner
from anomradar.scanners.dns import DnsScanner
from anomradar.scanners.ssl import SslScanner
from anomradar.exporters.json_exporter import JsonExporter
from anomradar.exporters.html_exporter import HtmlExporter


# Create Typer app
app = typer.Typer(
    name="anomradar",
    help="AnomRadar v2 - Production-ready security scanner toolkit",
    add_completion=True,
)

console = Console()


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Global exception handler that writes errors to file and exits gracefully.
    
    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    # Don't handle KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Create error log directory
    error_dir = Path("~/.anomradar").expanduser()
    error_dir.mkdir(parents=True, exist_ok=True)
    error_file = error_dir / "last_error.json"
    
    # Prepare error data
    error_data = {
        "timestamp": datetime.now().isoformat(),
        "type": exc_type.__name__,
        "message": str(exc_value),
        "traceback": "".join(traceback.format_tb(exc_traceback))
    }
    
    # Write error to file
    try:
        with open(error_file, "w") as f:
            json.dump(error_data, f, indent=2)
    except Exception:
        pass
    
    # Print friendly error message
    console.print("\n[bold red]❌ AnomRadar encountered an unexpected error[/bold red]\n")
    console.print(f"[yellow]Error type:[/yellow] {exc_type.__name__}")
    console.print(f"[yellow]Message:[/yellow] {exc_value}\n")
    console.print(f"[dim]Error details saved to: {error_file}[/dim]\n")
    
    # Provide actionable hints
    console.print("[bold cyan]💡 Troubleshooting hints:[/bold cyan]")
    if "connection" in str(exc_value).lower() or "timeout" in str(exc_value).lower():
        console.print("  • Check your internet connection")
        console.print("  • Verify the target domain is accessible")
        console.print("  • Try increasing timeout in configuration")
    elif "permission" in str(exc_value).lower():
        console.print("  • Check file/directory permissions")
        console.print("  • Ensure ~/.anomradar directory is writable")
    elif "module" in str(exc_value).lower() or "import" in str(exc_value).lower():
        console.print("  • Run: pip install -r requirements.txt")
        console.print("  • Verify Python version is 3.8 or higher")
    else:
        console.print("  • Run with --debug flag for detailed logs")
        console.print("  • Check logs in ~/.anomradar/logs/")
        console.print("  • Report issue: https://github.com/AnomFIN/AnomRadar/issues")
    
    console.print()
    sys.exit(1)


# Install global exception handler
sys.excepthook = global_exception_handler


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target domain or URL to scan"),
    scanners: Optional[List[str]] = typer.Option(
        None,
        "--scanner",
        "-s",
        help="Specific scanners to run (http, dns, ssl). Default: all"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output filename for report"
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format (json, html)"
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable caching"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging"
    ),
):
    """
    Scan a target domain for security issues.
    
    Examples:
        anomradar scan example.com
        anomradar scan https://example.com --scanner http --scanner dns
        anomradar scan example.com --format html --output report.html
    """
    # Setup logging
    config = get_config()
    setup_logging(
        level=config.logging.level,
        log_file=str(config.get_log_file()),
        console_output=True,
        debug=debug
    )
    logger = get_logger()
    
    logger.info(f"Starting scan: {target}")
    
    # Display banner
    console.print(Panel.fit(
        f"[bold cyan]AnomRadar v{__version__}[/bold cyan]\n"
        f"[dim]Security Scanner Toolkit[/dim]",
        border_style="cyan"
    ))
    
    console.print(f"\n[bold]Target:[/bold] {target}")
    
    # Determine which scanners to run
    available_scanners = ["http", "dns", "ssl"]
    if scanners:
        selected_scanners = [s.lower() for s in scanners if s.lower() in available_scanners]
    else:
        selected_scanners = available_scanners
    
    console.print(f"[bold]Scanners:[/bold] {', '.join(selected_scanners)}\n")
    
    # Initialize cache
    cache = None if no_cache else Cache(
        cache_dir=str(config.get_cache_dir()),
        ttl=config.cache.ttl,
        enabled=config.cache.enabled
    )
    
    # Run scans
    results = {}
    
    async def run_scans():
        tasks = []
        
        if "http" in selected_scanners:
            console.print("🌐 Running HTTP scanner...")
            http_scanner = HttpScanner(config=config, cache=cache)
            tasks.append(("http", http_scanner.scan(target)))
        
        if "dns" in selected_scanners:
            console.print("🔍 Running DNS scanner...")
            dns_scanner = DnsScanner(config=config, cache=cache)
            tasks.append(("dns", dns_scanner.scan(target)))
        
        if "ssl" in selected_scanners:
            console.print("🔒 Running SSL scanner...")
            ssl_scanner = SslScanner(config=config, cache=cache)
            tasks.append(("ssl", ssl_scanner.scan(target)))
        
        # Execute all scans
        for scanner_name, task in tasks:
            try:
                result = await task
                results[scanner_name] = result
                
                # Display status
                status_color = {
                    "success": "green",
                    "partial": "yellow",
                    "failed": "red"
                }.get(result["status"], "white")
                
                console.print(f"  [{status_color}]✓ {scanner_name.upper()}: {result['status']}[/{status_color}]")
            except Exception as e:
                logger.error(f"Scanner {scanner_name} failed: {e}")
                console.print(f"  [red]✗ {scanner_name.upper()}: failed[/red]")
    
    # Run async scans
    asyncio.run(run_scans())
    
    console.print()
    
    # Display results summary
    table = Table(title="Scan Results Summary", show_header=True, header_style="bold cyan")
    table.add_column("Scanner", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Findings", justify="right")
    
    for scanner_name, result in results.items():
        status_emoji = {"success": "✓", "partial": "⚠", "failed": "✗"}.get(result["status"], "?")
        findings_count = len(result.get("signals", []))
        table.add_row(
            scanner_name.upper(),
            f"{status_emoji} {result['status']}",
            str(findings_count)
        )
    
    console.print(table)
    console.print()
    
    # Export results
    scan_data = {
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "metadata": {
            "version": __version__,
            "scanners": selected_scanners
        }
    }
    
    if format.lower() == "json":
        exporter = JsonExporter(output_dir=str(config.get_report_dir()))
        output_file = exporter.export(scan_data, filename=output)
        console.print(f"[green]✓ JSON report saved:[/green] {output_file}")
    elif format.lower() == "html":
        exporter = HtmlExporter(output_dir=str(config.get_report_dir()))
        output_file = exporter.export(scan_data, filename=output)
        console.print(f"[green]✓ HTML report saved:[/green] {output_file}")
    
    logger.info(f"Scan completed: {target}")


@app.command()
def tui():
    """
    Launch the interactive TUI (Text User Interface).
    
    Note: TUI is experimental. Use CLI commands for stable operation.
    """
    try:
        from anomradar.tui.app import run_tui
        run_tui()
    except ImportError as e:
        console.print("[red]Error: TUI dependencies not available[/red]")
        console.print(f"[dim]{e}[/dim]")
        console.print("\nInstall with: pip install textual")
        raise typer.Exit(1)


@app.command()
def report(
    input_file: str = typer.Argument(..., help="Input JSON scan results file"),
    format: str = typer.Option("html", "--format", "-f", help="Output format (html, json)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output filename"),
):
    """
    Generate a report from existing scan results.
    
    Example:
        anomradar report scan_results.json --format html
    """
    config = get_config()
    
    try:
        # Load scan results
        with open(input_file, "r") as f:
            data = json.load(f)
        
        # Extract scan results
        if "scan_results" in data:
            scan_data = data["scan_results"]
        else:
            scan_data = data
        
        # Export
        if format.lower() == "html":
            exporter = HtmlExporter(output_dir=str(config.get_report_dir()))
            output_file = exporter.export(scan_data, filename=output)
            console.print(f"[green]✓ HTML report generated:[/green] {output_file}")
        elif format.lower() == "json":
            exporter = JsonExporter(output_dir=str(config.get_report_dir()))
            output_file = exporter.export(scan_data, filename=output)
            console.print(f"[green]✓ JSON report generated:[/green] {output_file}")
        else:
            console.print(f"[red]Unknown format: {format}[/red]")
            raise typer.Exit(1)
    
    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {input_file}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def self_check():
    """
    Run self-diagnostics to verify AnomRadar installation.
    
    Checks:
    - Configuration files
    - Required directories
    - Dependencies
    - Cache functionality
    """
    console.print(Panel.fit(
        "[bold cyan]AnomRadar Self-Check[/bold cyan]\n"
        "[dim]Verifying installation...[/dim]",
        border_style="cyan"
    ))
    
    checks = []
    
    # Check 1: Configuration
    try:
        config = get_config()
        checks.append(("Configuration", "✓", "green"))
    except Exception as e:
        checks.append(("Configuration", f"✗ {e}", "red"))
    
    # Check 2: Directories
    try:
        config.ensure_directories()
        checks.append(("Directories", "✓", "green"))
    except Exception as e:
        checks.append(("Directories", f"✗ {e}", "red"))
    
    # Check 3: Cache
    try:
        cache = Cache(cache_dir=str(config.get_cache_dir()), ttl=60, enabled=True)
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        if value == "test_value":
            checks.append(("Cache", "✓", "green"))
        else:
            checks.append(("Cache", "✗ Read/write failed", "red"))
    except Exception as e:
        checks.append(("Cache", f"✗ {e}", "red"))
    
    # Check 4: Scanners
    try:
        from anomradar.scanners.http import HttpScanner
        from anomradar.scanners.dns import DnsScanner
        from anomradar.scanners.ssl import SslScanner
        checks.append(("Scanners", "✓", "green"))
    except Exception as e:
        checks.append(("Scanners", f"✗ {e}", "red"))
    
    # Check 5: Exporters
    try:
        from anomradar.exporters.json_exporter import JsonExporter
        from anomradar.exporters.html_exporter import HtmlExporter
        checks.append(("Exporters", "✓", "green"))
    except Exception as e:
        checks.append(("Exporters", f"✗ {e}", "red"))
    
    # Display results
    console.print()
    for check_name, result, color in checks:
        console.print(f"  [{color}]{result}[/{color}] {check_name}")
    
    console.print()
    
    # Overall status
    all_passed = all(result == "✓" for _, result, _ in checks)
    if all_passed:
        console.print("[bold green]✓ All checks passed![/bold green]")
        console.print(f"\n[dim]AnomRadar v{__version__} is ready to use.[/dim]")
    else:
        console.print("[bold red]✗ Some checks failed[/bold red]")
        console.print("\n[yellow]Run with --debug for more details[/yellow]")
        raise typer.Exit(1)


@app.command()
def doctor():
    """
    Run diagnostics and provide recommendations for system health.
    
    More comprehensive than self-check, includes:
    - System information
    - Configuration validation
    - Cache statistics
    - Log file analysis
    """
    console.print(Panel.fit(
        "[bold cyan]AnomRadar Doctor[/bold cyan]\n"
        "[dim]Running comprehensive diagnostics...[/dim]",
        border_style="cyan"
    ))
    
    config = get_config()
    
    # System info
    console.print("\n[bold]System Information:[/bold]")
    console.print(f"  Python: {sys.version.split()[0]}")
    console.print(f"  Platform: {sys.platform}")
    console.print(f"  AnomRadar: v{__version__}")
    
    # Configuration
    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Cache: {'enabled' if config.cache.enabled else 'disabled'}")
    console.print(f"  Cache TTL: {config.cache.ttl}s")
    console.print(f"  Cache Dir: {config.get_cache_dir()}")
    console.print(f"  Reports Dir: {config.get_report_dir()}")
    console.print(f"  Log File: {config.get_log_file()}")
    
    # Cache statistics
    console.print("\n[bold]Cache Statistics:[/bold]")
    cache_dir = config.get_cache_dir()
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        console.print(f"  Entries: {len(cache_files)}")
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in cache_files)
        console.print(f"  Size: {total_size / 1024:.2f} KB")
    else:
        console.print("  [yellow]Cache directory not yet created[/yellow]")
    
    # Reports
    console.print("\n[bold]Reports:[/bold]")
    report_dir = config.get_report_dir()
    if report_dir.exists():
        reports = list(report_dir.glob("*.json")) + list(report_dir.glob("*.html"))
        console.print(f"  Total reports: {len(reports)}")
    else:
        console.print("  [yellow]Reports directory not yet created[/yellow]")
    
    # Recommendations
    console.print("\n[bold cyan]💡 Recommendations:[/bold cyan]")
    recommendations = []
    
    if not config.cache.enabled:
        recommendations.append("Consider enabling cache for better performance")
    
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        if len(cache_files) > 100:
            recommendations.append("Cache has many entries, consider cleanup")
    
    if recommendations:
        for rec in recommendations:
            console.print(f"  • {rec}")
    else:
        console.print("  [green]✓ Everything looks good![/green]")
    
    console.print()


@app.command()
def version():
    """Display AnomRadar version information."""
    console.print(f"[bold cyan]AnomRadar[/bold cyan] version [green]{__version__}[/green]")
    console.print("\nHomepage: https://github.com/AnomFIN/AnomRadar")


@app.callback()
def main():
    """
    AnomRadar v2 - Production-ready security scanner toolkit.
    
    A resilient CLI/TUI scanner with modular architecture,
    intelligent caching, and brand-grade reporting.
    """
    pass


if __name__ == "__main__":
    app()
