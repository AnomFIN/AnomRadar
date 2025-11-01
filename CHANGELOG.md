# Changelog

All notable changes to AnomRadar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-11-01

### Added - AnomRadar v2 Complete Rewrite

#### Core Infrastructure
- **Layered Configuration System**: Pydantic-based settings with .env and TOML support
- **File-based Caching**: TTL-based caching system in ~/.anomradar/cache
- **Rich Logging**: Beautiful console output with file logging and debug mode
- **Global Exception Handler**: Crash protection with actionable error hints
- **Production-ready Error Handling**: Graceful degradation for all scanners

#### Scanners
- **HTTP Scanner**: Using httpx for async HTTP/HTTPS scanning
  - Security header analysis (HSTS, CSP, X-Frame-Options, etc.)
  - Response time measurement
  - Redirect detection
  - Status code validation
- **DNS Scanner**: Using dnspython for comprehensive DNS analysis
  - A/AAAA, MX, TXT, NS, SOA records
  - SPF and DMARC detection
  - Email security validation
- **SSL Scanner**: Native Python SSL certificate analysis
  - Certificate expiration checking
  - Issuer validation
  - Self-signed certificate detection
  - Subject alternative names

#### CLI Interface
- **Typer-based CLI**: Modern command-line interface
  - `scan` - Execute security scans
  - `tui` - Launch interactive terminal UI
  - `report` - Generate reports from scan results
  - `self-check` - Installation diagnostics
  - `doctor` - Comprehensive system health check
  - `version` - Display version information
- **Global --debug Flag**: Enhanced debugging with full trace logging

#### TUI (Text User Interface)
- **Textual-based Interactive UI**: Reactive terminal interface
- **Real-time Scan Execution**: Live scan progress and results
- **Keyboard Shortcuts**: Quick access to common operations
- **Safe Event Handlers**: Crash-protected interactive elements

#### Exporters
- **JSON Exporter**: High-performance orjson-based JSON export
- **HTML Exporter**: Jinja2-templated brand-grade HTML reports
  - Professional gradient design
  - Color-coded severity levels
  - Responsive layout
  - Print-friendly styling
  - Fallback template support

#### Installation
- **Interactive Installer Wizard** (scripts/asennus.py):
  - Python version validation
  - Virtual environment creation
  - Dependency installation
  - Configuration file setup
  - Directory structure creation
  - Shell alias creation (Unix)
  - Post-install self-check
- **Windows Support**: Batch wrapper (scripts/asennus.bat)
- **One-command Setup**: Automated installation process

#### Testing & CI
- **Pytest Test Suite**: Comprehensive test coverage
  - Configuration tests
  - Scanner tests with example.com
  - Graceful error handling validation
- **GitHub Actions CI**: Multi-platform testing
  - Python 3.8, 3.9, 3.10, 3.11 matrix
  - Ruff linting
  - Security scanning with safety
  - Installer testing on Ubuntu, Windows, macOS
  - Integration tests

#### Documentation
- **Updated README.md**: Complete v2 quickstart guide
- **CHANGELOG.md**: This file
- **TUI README**: Detailed TUI usage guide
- **Configuration Examples**: .env.example and anomradar.toml.example
- **Inline Documentation**: Comprehensive docstrings

#### Branding
- **AnomFIN Logo**: SVG brand asset (assets/brand/anomfin.svg)
- **Professional Report Templates**: Gradient design with corporate styling
- **Consistent Visual Identity**: Purple/blue color scheme throughout

### Changed from v1.x

#### Architecture
- **Language**: Migrated from TypeScript/Node.js to Python for v2 scanners
- **Framework**: New standalone CLI/TUI toolkit (v1 remains as backend service)
- **Configuration**: From .env-only to layered .env + TOML
- **Caching**: From in-memory to persistent file-based cache
- **Logging**: From Winston to Rich

#### Design Philosophy
- **Resilience First**: All scanners degrade gracefully on errors
- **User Experience**: Rich terminal output and interactive TUI
- **Production Ready**: Global exception handling, comprehensive tests, CI/CD
- **Modular Architecture**: Clean separation of concerns

### Technical Details

#### Dependencies
- **Core**: typer 0.9.0, pydantic 2.5.0, pydantic-settings 2.1.0
- **TUI**: textual 0.44.1, rich 13.7.0
- **Scanners**: httpx 0.25.2, dnspython 2.4.2
- **Exporters**: orjson 3.9.10, jinja2 3.1.2
- **Testing**: pytest 7.4.3, pytest-asyncio 0.21.1
- **Linting**: ruff 0.1.8

#### Requirements
- Python 3.8 or higher
- Internet connection for scanning
- ~50MB disk space for installation

### Compatibility

AnomRadar v2 is a new Python-based CLI/TUI toolkit that complements the existing
v1 TypeScript/Node.js backend. Both versions can coexist:

- **v1**: Backend scanner service (Node.js + TypeScript)
- **v2**: Standalone CLI/TUI toolkit (Python)

### Migration Guide

If migrating from v1 or starting fresh:

1. Install v2: `python scripts/asennus.py`
2. Configure: Edit `~/.anomradar/anomradar.toml`
3. Test: Run `anomradar self-check`
4. Scan: Run `anomradar scan example.com`

### Security

- No active attacks or intrusive testing
- Passive reconnaissance only
- Network error tolerance
- Secure credential handling
- No secrets in code

### Known Issues

- TUI is experimental; CLI commands recommended for production
- Some network timeouts may occur on slow connections
- Windows installer requires manual venv activation

### Future Roadmap

- Additional scanner modules (WHOIS, subdomain enumeration)
- Cloud export targets (S3, Azure Blob)
- Scheduled scanning
- Web dashboard integration
- Plugin system for custom scanners

### Credits

- Built by AnomFIN team
- Inspired by OWASP ZAP, Nikto, and modern OSINT tools
- Thanks to all open-source contributors

---

## [1.x] - Previous Versions

See git history for v1.x changes (TypeScript/Node.js backend).

[2.0.0]: https://github.com/AnomFIN/AnomRadar/releases/tag/v2.0.0
