AnomRadar v2 - Text User Interface (TUI)
==========================================

The TUI provides an interactive terminal interface for running security scans.

Features:
---------
- Real-time scan execution and monitoring
- Interactive target input
- Live result display with color-coded findings
- Built-in self-check diagnostic
- Keyboard shortcuts for quick access

Usage:
------
Launch the TUI with:
    anomradar tui

Or directly:
    python -m anomradar.tui.app

Keyboard Shortcuts:
-------------------
- 'q' - Quit the application
- 'c' - Clear the log
- 's' - Focus on input field
- 'r' - Run self-check diagnostic
- Enter - Submit target and start scan

Navigation:
-----------
1. Enter target domain in the input field
2. Press Enter or click "Scan" button
3. Watch results appear in real-time
4. View findings for each scanner (HTTP, DNS, SSL)
5. Clear log when needed

Requirements:
-------------
The TUI requires the 'textual' package:
    pip install textual

For best experience, use a modern terminal with:
- Unicode support
- 256 colors or true color
- Minimum 80x24 terminal size

Troubleshooting:
----------------
If the TUI doesn't display correctly:
- Ensure your terminal supports Unicode
- Try increasing terminal size
- Check terminal color support
- Run 'anomradar doctor' for diagnostics

For stable operation, use CLI commands instead:
    anomradar scan example.com

Note:
-----
The TUI is experimental. For production use,
CLI commands provide more stability and automation options.
