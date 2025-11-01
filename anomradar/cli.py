"""AnomRadar v2 CLI - Command-line interface with Typer

Provides commands: scan, tui, report, self-check, doctor
with global exception handler writing errors to ~/.anomradar/last_error.json
"""

import json
import sys
import traceback
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from functools import wraps

import typer
from rich.console import Console

from anomradar import __version__
from anomradar.core.config import Config
from anomradar.core.logging import setup_logging
from anomradar.core.cache import FileCache

app = typer.Typer(
    name="anomradar",
    help="AnomRadar v2 - Production-Ready Security Scanner Toolkit",
    add_completion=False,
)
console = Console()


def write_error_log(error: Exception, context: str = "") -> None:
    """Write error details to ~/.anomradar/last_error.json
    
    Args:
        error: Exception that occurred
        context: Additional context about where the error occurred
    """
    error_dir = Path.home() / ".anomradar"
    error_dir.mkdir(parents=True, exist_ok=True)
    error_file = error_dir / "last_error.json"
    
    error_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": __version__,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "traceback": traceback.format_exc(),
    }
    
    try:
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)
    except Exception:
        # If we can't write the error log, just print to stderr
        console.print(f"[red]Failed to write error log to {error_file}[/red]", file=sys.stderr)


def global_exception_handler(func):
    """Decorator to handle exceptions globally and write to error log"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            write_error_log(e, context=func.__name__)
            console.print(f"[red bold]Error:[/red bold] {str(e)}", file=sys.stderr)
            console.print("[yellow]Error details written to ~/.anomradar/last_error.json[/yellow]")
            sys.exit(1)
    return wrapper


@app.command()
@global_exception_handler
def scan(
    target: str = typer.Argument(..., help="Target domain or IP to scan"),
    scanners: Optional[List[str]] = typer.Option(
        None, "--scanner", "-s",
        help="Specific scanners to run (http, dns, ssl). Run all if not specified."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output file path (JSON format)"
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache",
        help="Disable cache for this scan"
    ),
) -> None:
    """Run security scan on target domain or IP
    
    Examples:
        anomradar scan example.com
        anomradar scan example.com --scanner http --scanner dns
        anomradar scan example.com -o results.json
    """
    config = Config.load()
    config.ensure_directories()
    logger = setup_logging(config)
    
    logger.info(f"Starting scan of {target}")
    console.print(f"[cyan]Scanning:[/cyan] {target}")
    
    # Import scanners here to avoid circular imports
    from anomradar.scanners import run_scan
    
    # Run scan
    results = run_scan(
        target=target,
        scanner_names=scanners,
        config=config,
        use_cache=not no_cache
    )
    
    # Display results
    console.print(f"\n[green]Scan completed:[/green] {target}")
    console.print("[cyan]Results:[/cyan]")
    
    for scanner_name, result in results.items():
        status = "[green]✓[/green]" if result.get("success") else "[red]✗[/red]"
        console.print(f"  {status} {scanner_name}: {result.get('message', 'No message')}")
    
    # Save to file if requested
    if output:
        from anomradar.exporters.json_exporter import export_json
        export_json(results, output)
        console.print(f"\n[green]Results saved to:[/green] {output}")
    
    logger.info(f"Scan completed for {target}")


@app.command()
@global_exception_handler
def tui() -> None:
    """Launch interactive TUI (Text User Interface)
    
    Provides an interactive terminal interface for managing scans.
    """
    console.print("[cyan]Launching AnomRadar TUI...[/cyan]")
    
    from anomradar.tui.app import run_tui
    run_tui()


@app.command()
@global_exception_handler
def report(
    scan_file: Path = typer.Argument(..., help="Path to scan results JSON file"),
    output: Path = typer.Option(
        None, "--output", "-o",
        help="Output file path (HTML format)"
    ),
    format: str = typer.Option(
        "html", "--format", "-f",
        help="Report format (html or json)"
    ),
) -> None:
    """Generate report from scan results
    
    Examples:
        anomradar report results.json
        anomradar report results.json -o report.html
        anomradar report results.json -f json -o report.json
    """
    if not scan_file.exists():
        console.print(f"[red]Error:[/red] File not found: {scan_file}", file=sys.stderr)
        sys.exit(1)
    
    console.print(f"[cyan]Generating {format} report from:[/cyan] {scan_file}")
    
    # Load scan results
    with open(scan_file, 'r') as f:
        results = json.load(f)
    
    # Generate report based on format
    if format == "html":
        from anomradar.exporters.html_exporter import export_html
        output_path = output or scan_file.with_suffix(".html")
        export_html(results, output_path)
    elif format == "json":
        from anomradar.exporters.json_exporter import export_json
        output_path = output or scan_file.with_suffix(".formatted.json")
        export_json(results, output_path)
    else:
        console.print(f"[red]Error:[/red] Unknown format: {format}", file=sys.stderr)
        sys.exit(1)
    
    console.print(f"[green]Report generated:[/green] {output_path}")


@app.command("self-check")
@global_exception_handler
def self_check() -> None:
    """Run self-diagnostics and verify installation
    
    Checks configuration, dependencies, and system requirements.
    """
    console.print("[cyan bold]AnomRadar Self-Check[/cyan bold]\n")
    
    # Check version
    console.print(f"[green]✓[/green] Version: {__version__}")
    
    # Check configuration
    try:
        config = Config.load()
        console.print("[green]✓[/green] Configuration loaded successfully")
        
        # Check directories
        config.ensure_directories()
        console.print(f"[green]✓[/green] Cache directory: {config.cache_dir}")
        console.print(f"[green]✓[/green] Data directory: {config.data_dir}")
    except Exception as e:
        console.print(f"[red]✗[/red] Configuration error: {e}")
        return
    
    # Check cache
    try:
        cache = FileCache(config.cache_dir, config.cache_ttl)
        cache.set("self_check", "test")
        value = cache.get("self_check")
        if value == "test":
            console.print("[green]✓[/green] Cache working correctly")
        else:
            console.print("[yellow]![/yellow] Cache test failed")
    except Exception as e:
        console.print(f"[red]✗[/red] Cache error: {e}")
    
    # Check scanners
    console.print("\n[cyan]Scanner Status:[/cyan]")
    from anomradar.scanners import get_available_scanners
    scanners = get_available_scanners()
    for scanner_name in scanners:
        console.print(f"[green]✓[/green] {scanner_name} scanner available")
    
    console.print("\n[green bold]Self-check completed![/green bold]")


@app.command()
@global_exception_handler
def doctor() -> None:
    """Diagnose common issues and suggest fixes
    
    Provides detailed diagnostics and troubleshooting information.
    """
    console.print("[cyan bold]AnomRadar Doctor[/cyan bold]\n")
    
    issues_found = 0
    
    # Check Python version
    import sys
    py_version = sys.version_info
    if py_version >= (3, 8):
        console.print(f"[green]✓[/green] Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        console.print(f"[red]✗[/red] Python version {py_version.major}.{py_version.minor} is too old. Requires Python 3.8+")
        issues_found += 1
    
    # Check dependencies
    console.print("\n[cyan]Checking dependencies...[/cyan]")
    required_modules = ["typer", "pydantic", "httpx", "dnspython", "jinja2", "orjson", "textual"]
    for module in required_modules:
        try:
            __import__(module)
            console.print(f"[green]✓[/green] {module} installed")
        except ImportError:
            console.print(f"[red]✗[/red] {module} not found - run: pip install {module}")
            issues_found += 1
    
    # Check configuration files
    console.print("\n[cyan]Checking configuration...[/cyan]")
    env_file = Path(".env")
    toml_file = Path("anomradar.toml")
    
    if env_file.exists():
        console.print("[green]✓[/green] .env file found")
    else:
        console.print("[yellow]![/yellow] .env file not found (optional)")
        console.print("    [dim]Create from: cp .env.example .env[/dim]")
    
    if toml_file.exists():
        console.print("[green]✓[/green] anomradar.toml file found")
    else:
        console.print("[yellow]![/yellow] anomradar.toml file not found (optional)")
        console.print("    [dim]Create from: cp anomradar.toml.example anomradar.toml[/dim]")
    
    # Check directories
    console.print("\n[cyan]Checking directories...[/cyan]")
    anomradar_dir = Path.home() / ".anomradar"
    if anomradar_dir.exists():
        console.print("[green]✓[/green] ~/.anomradar directory exists")
        
        # Check subdirectories
        cache_dir = anomradar_dir / "cache"
        data_dir = anomradar_dir / "data"
        
        if cache_dir.exists():
            cache_files = list(cache_dir.glob("*.json"))
            console.print(f"[green]✓[/green] Cache directory ({len(cache_files)} files)")
        else:
            console.print("[yellow]![/yellow] Cache directory will be created on first use")
        
        if data_dir.exists():
            console.print("[green]✓[/green] Data directory exists")
        else:
            console.print("[yellow]![/yellow] Data directory will be created on first use")
    else:
        console.print("[yellow]![/yellow] ~/.anomradar directory will be created on first use")
    
    # Summary
    console.print()
    if issues_found == 0:
        console.print("[green bold]✓ No issues found![/green bold]")
    else:
        console.print(f"[yellow bold]! Found {issues_found} issue(s) - please address them above[/yellow bold]")


@app.command()
def version() -> None:
    """Show version information"""
    console.print(f"AnomRadar v{__version__}")


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()
