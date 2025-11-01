# Changelog

All notable changes to AnomRadar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-01

### Added - AnomRadar v2 Complete Rewrite

#### Core Infrastructure
- **Python-based architecture** replacing Node.js backend
- **Typer CLI framework** with 5 commands: scan, tui, report, self-check, doctor
- **Global exception handler** writing errors to ~/.anomradar/last_error.json
- **Pydantic configuration system** merging .env and anomradar.toml files
- **File-based cache** with TTL support in ~/.anomradar/cache
- **Structured JSON logging** with colored console output

#### Scanner System
- **HTTP Scanner**: Status codes, headers, security headers, redirect chains
- **DNS Scanner**: A, AAAA, MX, TXT, NS, SOA, CNAME records
- **SSL/TLS Scanner**: Certificate validation, expiry checks, cipher info
- **Graceful degradation**: All scanners handle errors without crashing
- **Structured output**: Consistent dict format across all scanners

#### Export & Reporting
- **JSON Exporter**: Fast serialization with orjson, pretty-printing
- **HTML Exporter**: Professional reports using Jinja2 templates
- **Fallback templates**: Graceful degradation when dependencies missing
- **Multiple formats**: JSON and HTML report generation

#### TUI (Terminal User Interface)
- **Textual-based TUI**: Modern, interactive terminal interface
- **Safe event handlers**: All handlers wrapped with exception handling
- **Real-time scanning**: Interactive domain input and live results
- **Keyboard shortcuts**: q (quit), c (clear), Enter (scan)

#### Installers
- **asennus.py**: Interactive Python installer for Linux/macOS/Unix
- **asennus.bat**: Interactive batch installer for Windows
- **One-command setup**: Handles dependencies, config, and directories
- **Self-check integration**: Automatic verification after install

#### Testing & CI
- **Pytest test suite**: Comprehensive tests using example.com
- **Config tests**: Validation, path expansion, TOML/env loading
- **Scanner tests**: All three scanners with real-world testing
- **CI/CD workflow**: GitHub Actions with ruff linting and pytest
- **Multi-version testing**: Python 3.8 through 3.12
- **Code coverage**: Automated coverage reporting

#### Configuration
- **Environment variables**: .env file support with ANOMRADAR_ prefix
- **TOML configuration**: Advanced settings in anomradar.toml
- **Flexible merging**: Environment > TOML > defaults priority
- **Example files**: .env.example and anomradar.toml.example provided

#### Documentation
- **Updated README.md**: Complete v2 documentation
- **TUI README**: Usage instructions for terminal interface
- **Installer docs**: Inline help and completion messages
- **Code comments**: Comprehensive docstrings throughout

#### Branding
- **AnomFIN SVG logo**: Animated radar with shield and lock
- **Professional design**: Gradient colors, modern aesthetic
- **Responsive**: Works at any size

### Changed
- Complete rewrite from Node.js/TypeScript to Python
- New project structure with anomradar/ package
- Simplified installation process (one command)
- Improved error handling and logging
- Modern CLI with rich terminal output

### Technical Details
- **Python 3.8+** required
- **Dependencies**: typer, pydantic, httpx, dnspython, jinja2, orjson, textual
- **Pinned versions**: All dependencies use exact versions for reproducibility
- **Cross-platform**: Linux, macOS, Windows support
- **Cache directory**: ~/.anomradar/cache with configurable TTL
- **Data directory**: ~/.anomradar/data for persistent storage
- **Log directory**: ~/.anomradar/logs for structured logging

### Breaking Changes
- Previous Node.js backend is replaced entirely
- API endpoints are not part of v2 (CLI/TUI focus)
- Configuration format changed from Node.js .env to Python .env + TOML
- Database removed in favor of file-based caching
- New command-line interface (incompatible with v1)

## [1.0.0] - Previous

See git history for AnomRadar v1 changes (Node.js/TypeScript/PHP stack).
