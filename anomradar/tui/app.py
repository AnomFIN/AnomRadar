"""Textual TUI application for AnomRadar v2

Interactive terminal interface with safe exception handlers.
"""

import logging
from typing import Optional

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Header, Footer, Button, Input, Static, Label
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

logger = logging.getLogger("anomradar.tui")


class ScannerApp(App):
    """AnomRadar TUI Application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    #input-container {
        height: auto;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }
    
    #results-container {
        height: 1fr;
        padding: 1;
        margin-top: 1;
        background: $panel;
        border: solid $accent;
    }
    
    Input {
        width: 70%;
    }
    
    Button {
        margin-left: 1;
    }
    
    .status {
        margin-top: 1;
        padding: 1;
        background: $boost;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "clear", "Clear"),
        ("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self):
        super().__init__()
        self.scan_results: Optional[dict] = None
    
    def compose(self) -> ComposeResult:
        """Compose the UI"""
        try:
            yield Header()
            
            with Container(id="main-container"):
                with Vertical(id="input-container"):
                    yield Label("🔒 AnomRadar v2 - Security Scanner")
                    with Horizontal():
                        yield Input(placeholder="Enter domain to scan (e.g., example.com)", id="target-input")
                        yield Button("Scan", variant="primary", id="scan-btn")
                        yield Button("Clear", variant="default", id="clear-btn")
                
                with Vertical(id="results-container"):
                    yield Static("Ready to scan. Enter a domain above and click Scan.", id="results")
            
            yield Footer()
        except Exception as e:
            logger.error(f"Error composing TUI: {e}", exc_info=True)
            raise
    
    def on_button_pressed(self, event: "Button.Pressed") -> None:
        """Handle button press events with safe exception handling"""
        try:
            if event.button.id == "scan-btn":
                self.action_scan()
            elif event.button.id == "clear-btn":
                self.action_clear()
        except Exception as e:
            logger.error(f"Error handling button press: {e}", exc_info=True)
            self.update_results(f"Error: {str(e)}", error=True)
    
    def on_input_submitted(self, event: "Input.Submitted") -> None:
        """Handle input submission (Enter key) with safe exception handling"""
        try:
            if event.input.id == "target-input":
                self.action_scan()
        except Exception as e:
            logger.error(f"Error handling input submission: {e}", exc_info=True)
            self.update_results(f"Error: {str(e)}", error=True)
    
    def action_scan(self) -> None:
        """Perform scan action with safe exception handling"""
        try:
            input_widget = self.query_one("#target-input", Input)
            target = input_widget.value.strip()
            
            if not target:
                self.update_results("Please enter a domain to scan.", error=True)
                return
            
            self.update_results(f"Scanning {target}...\n\nThis may take a moment...")
            
            # Import and run scan
            from anomradar.core.config import Config
            from anomradar.scanners import run_scan
            
            config = Config.load()
            results = run_scan(target, config=config)
            
            # Format results
            output = self.format_results(target, results)
            self.update_results(output)
            self.scan_results = results
            
        except Exception as e:
            logger.error(f"Error during scan: {e}", exc_info=True)
            self.update_results(f"Scan failed: {str(e)}", error=True)
    
    def action_clear(self) -> None:
        """Clear results with safe exception handling"""
        try:
            self.update_results("Ready to scan. Enter a domain above and click Scan.")
            input_widget = self.query_one("#target-input", Input)
            input_widget.value = ""
            self.scan_results = None
        except Exception as e:
            logger.error(f"Error clearing: {e}", exc_info=True)
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()
    
    def format_results(self, target: str, results: dict) -> str:
        """Format scan results for display"""
        output = [f"Scan Results for: {target}\n"]
        output.append("=" * 60)
        
        for scanner_name, scanner_data in results.items():
            status = "✓ SUCCESS" if scanner_data.get("success") else "✗ FAILED"
            output.append(f"\n{scanner_name.upper()} Scanner: {status}")
            output.append(f"Message: {scanner_data.get('message', 'N/A')}")
            
            if scanner_data.get("warning"):
                output.append(f"⚠️  Warning: {scanner_data['warning']}")
            
            if scanner_data.get("data"):
                output.append("\nData:")
                data = scanner_data["data"]
                for key, value in data.items():
                    if isinstance(value, (list, dict)):
                        output.append(f"  {key}: {len(value) if isinstance(value, list) else len(value.keys())} items")
                    else:
                        output.append(f"  {key}: {value}")
            
            output.append("-" * 60)
        
        return "\n".join(output)
    
    def update_results(self, text: str, error: bool = False) -> None:
        """Update results display with safe exception handling"""
        try:
            results_widget = self.query_one("#results", Static)
            results_widget.update(text)
        except Exception as e:
            logger.error(f"Error updating results: {e}", exc_info=True)


def run_tui() -> None:
    """Run the TUI application with safe exception handling"""
    if not TEXTUAL_AVAILABLE:
        print("Error: Textual library not available.")
        print("Install with: pip install textual")
        return
    
    try:
        app = ScannerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nTUI interrupted by user.")
    except Exception as e:
        logger.error(f"TUI error: {e}", exc_info=True)
        print(f"TUI error: {e}")
        print("Check logs for details.")
