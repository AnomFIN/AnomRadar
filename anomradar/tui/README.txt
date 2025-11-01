# AnomRadar TUI (Text User Interface)

The TUI provides an interactive terminal interface for running security scans.

## Features

- Interactive domain input
- Real-time scan execution
- Formatted results display
- Keyboard shortcuts:
  - `q` or `Ctrl+C`: Quit
  - `c`: Clear results
  - `Enter`: Submit scan

## Usage

Launch the TUI with:

```bash
anomradar tui
```

Or with Python:

```bash
python -m anomradar.cli tui
```

## Requirements

- textual >= 0.44.1

Install with:
```bash
pip install textual
```

## Architecture

The TUI is built with Textual, a modern Python framework for building
terminal user interfaces. All event handlers include safe exception
handling to prevent crashes.

## Error Handling

All exceptions are caught and logged to ~/.anomradar/last_error.json
for debugging. The TUI will display user-friendly error messages.
