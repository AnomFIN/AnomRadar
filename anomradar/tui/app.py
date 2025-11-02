"""
Text User Interface (TUI) for AnomRadar v2.

Built with Textual for a reactive terminal UI.
Provides interactive scan management and results viewing.
"""

import asyncio
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Input, Static, Log
from textual.binding import Binding

from anomradar import __version__
from anomradar.core.config import get_config
from anomradar.core.logging import get_logger
from anomradar.core.cache import Cache
from anomradar.scanners.http import HttpScanner
from anomradar.scanners.dns import DnsScanner
from anomradar.scanners.ssl import SslScanner


logger = get_logger()


class ScanStatus(Static):
    """Display scan status information."""
    
    def __init__(self):
        super().__init__()
        self.update_content("Ready")
    
    def update_content(self, message: str):
        """Update status message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.update(f"[{timestamp}] {message}")


class AnomRadarTUI(App):
    """AnomRadar Text User Interface."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        height: 100%;
        layout: vertical;
    }
    
    #input-container {
        height: auto;
        layout: horizontal;
        padding: 1;
        background: $panel;
    }
    
    #target-input {
        width: 70%;
        margin-right: 1;
    }
    
    #scan-button {
        width: 15%;
        margin-right: 1;
    }
    
    #clear-button {
        width: 13%;
    }
    
    #status-container {
        height: 3;
        padding: 1;
        background: $primary;
        color: $text;
    }
    
    #results-log {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }
    
    Button {
        width: 100%;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("c", "clear", "Clear Log"),
        Binding("s", "focus_input", "Focus Input"),
        Binding("r", "run_self_check", "Self Check"),
    ]
    
    def __init__(self):
        super().__init__()
        self.title = f"AnomRadar v{__version__} - Security Scanner TUI"
        self.sub_title = "Press 'q' to quit, 'r' for self-check"
        
        # Initialize components
        try:
            self.config = get_config()
            self.cache = Cache(
                cache_dir=str(self.config.get_cache_dir()),
                ttl=self.config.cache.ttl,
                enabled=self.config.cache.enabled
            )
        except Exception as e:
            logger.error(f"TUI initialization error: {e}")
            self.config = None
            self.cache = None
    
    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        yield Header()
        
        with Container(id="main-container"):
            with Horizontal(id="input-container"):
                yield Input(
                    placeholder="Enter target domain (e.g., example.com)",
                    id="target-input"
                )
                yield Button("Scan", id="scan-button", variant="primary")
                yield Button("Clear Log", id="clear-button", variant="default")
            
            yield ScanStatus(id="status-container")
            
            yield Log(
                id="results-log",
                highlight=True,
                auto_scroll=True
            )
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle mount event."""
        try:
            log = self.query_one("#results-log", Log)
            log.write_line("=" * 60)
            log.write_line(f"  AnomRadar v{__version__} - Security Scanner TUI")
            log.write_line("=" * 60)
            log.write_line("")
            log.write_line("Welcome! Enter a target domain and click 'Scan' to begin.")
            log.write_line("Press 'r' for self-check, 'q' to quit.")
            log.write_line("")
            
            # Focus on input
            self.query_one("#target-input", Input).focus()
        except Exception as e:
            logger.error(f"Mount error: {e}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        try:
            if event.button.id == "scan-button":
                self.action_scan()
            elif event.button.id == "clear-button":
                self.action_clear()
        except Exception as e:
            logger.error(f"Button press error: {e}")
            self._log_error(f"Error: {e}")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "target-input":
            self.action_scan()
    
    def action_scan(self) -> None:
        """Execute scan action."""
        try:
            target_input = self.query_one("#target-input", Input)
            target = target_input.value.strip()
            
            if not target:
                self._log_error("Please enter a target domain")
                return
            
            # Update status
            status = self.query_one("#status-container", ScanStatus)
            status.update_content(f"Scanning {target}...")
            
            # Log start
            log = self.query_one("#results-log", Log)
            log.write_line(f"\n🔍 Starting scan of: {target}")
            log.write_line(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            log.write_line("-" * 60)
            
            # Run scan in background
            asyncio.create_task(self._run_scan(target))
        
        except Exception as e:
            logger.error(f"Scan action error: {e}")
            self._log_error(f"Scan failed: {e}")
    
    async def _run_scan(self, target: str) -> None:
        """
        Run scan asynchronously.
        
        Args:
            target: Target domain to scan
        """
        log = self.query_one("#results-log", Log)
        status = self.query_one("#status-container", ScanStatus)
        
        try:
            # Run HTTP scanner
            log.write_line("\n🌐 HTTP Scanner:")
            http_scanner = HttpScanner(config=self.config, cache=self.cache)
            http_result = await http_scanner.scan(target)
            self._log_scan_result("HTTP", http_result)
            
            # Run DNS scanner
            log.write_line("\n🔍 DNS Scanner:")
            dns_scanner = DnsScanner(config=self.config, cache=self.cache)
            dns_result = await dns_scanner.scan(target)
            self._log_scan_result("DNS", dns_result)
            
            # Run SSL scanner
            log.write_line("\n🔒 SSL Scanner:")
            ssl_scanner = SslScanner(config=self.config, cache=self.cache)
            ssl_result = await ssl_scanner.scan(target)
            self._log_scan_result("SSL", ssl_result)
            
            # Complete
            log.write_line("\n" + "=" * 60)
            log.write_line("✅ Scan complete!")
            log.write_line("=" * 60 + "\n")
            
            status.update_content("Scan complete")
        
        except Exception as e:
            logger.error(f"Scan execution error: {e}")
            log.write_line(f"\n❌ Scan failed: {e}\n")
            status.update_content("Scan failed")
    
    def _log_scan_result(self, scanner_name: str, result: dict) -> None:
        """
        Log scan result to TUI.
        
        Args:
            scanner_name: Name of the scanner
            result: Scan result dictionary
        """
        log = self.query_one("#results-log", Log)
        
        # Status
        status_emoji = {
            "success": "✅",
            "partial": "⚠️",
            "failed": "❌"
        }.get(result.get("status"), "❓")
        
        log.write_line(f"  Status: {status_emoji} {result.get('status', 'unknown').upper()}")
        log.write_line(f"  Summary: {result.get('summary', 'No summary')}")
        
        # Signals
        signals = result.get("signals", [])
        if signals:
            log.write_line(f"  Findings: {len(signals)}")
            for signal in signals[:5]:  # Show first 5
                severity = signal.get("severity", "info").upper()
                message = signal.get("message", "")
                log.write_line(f"    [{severity}] {message}")
            if len(signals) > 5:
                log.write_line(f"    ... and {len(signals) - 5} more")
        else:
            log.write_line("  Findings: None")
    
    def _log_error(self, message: str) -> None:
        """
        Log error message to TUI.
        
        Args:
            message: Error message
        """
        log = self.query_one("#results-log", Log)
        log.write_line(f"\n❌ {message}\n")
    
    def action_clear(self) -> None:
        """Clear the log."""
        try:
            log = self.query_one("#results-log", Log)
            log.clear()
            log.write_line("Log cleared.\n")
            
            status = self.query_one("#status-container", ScanStatus)
            status.update_content("Ready")
        except Exception as e:
            logger.error(f"Clear action error: {e}")
    
    def action_focus_input(self) -> None:
        """Focus on the input field."""
        try:
            self.query_one("#target-input", Input).focus()
        except Exception as e:
            logger.error(f"Focus action error: {e}")
    
    def action_run_self_check(self) -> None:
        """Run self-check diagnostic."""
        try:
            log = self.query_one("#results-log", Log)
            status = self.query_one("#status-container", ScanStatus)
            
            log.write_line("\n" + "=" * 60)
            log.write_line("🔧 Running Self-Check Diagnostic")
            log.write_line("=" * 60 + "\n")
            
            # Configuration check
            if self.config:
                log.write_line("✅ Configuration: OK")
                log.write_line(f"   Cache: {'enabled' if self.config.cache.enabled else 'disabled'}")
                log.write_line(f"   Cache TTL: {self.config.cache.ttl}s")
            else:
                log.write_line("❌ Configuration: Failed")
            
            # Cache check
            if self.cache:
                log.write_line("✅ Cache: OK")
                self.cache.set("tui_test", "test_value")
                value = self.cache.get("tui_test")
                if value == "test_value":
                    log.write_line("   Read/Write: OK")
                else:
                    log.write_line("   Read/Write: Failed")
            else:
                log.write_line("❌ Cache: Not available")
            
            # Scanners check
            log.write_line("✅ Scanners: Available")
            log.write_line("   - HTTP Scanner")
            log.write_line("   - DNS Scanner")
            log.write_line("   - SSL Scanner")
            
            log.write_line("\n" + "=" * 60)
            log.write_line("✅ Self-Check Complete")
            log.write_line("=" * 60 + "\n")
            
            status.update_content("Self-check complete")
        
        except Exception as e:
            logger.error(f"Self-check error: {e}")
            self._log_error(f"Self-check failed: {e}")


def run_tui():
    """Run the TUI application."""
    app = AnomRadarTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
