# AnomRadar v2

🔒 **Production-Ready CLI/TUI Security Scanner Toolkit**

AnomRadar v2 is a resilient Python-based security scanning toolkit with graceful error handling, structured output, and professional reporting. Built for security professionals who need reliable, reproducible scans.

## ⚠️ Important Notice

**AnomRadar performs only PASSIVE security scanning. No active attacks or intrusive testing are performed.**

- ✅ Passive HTTP/HTTPS analysis
- ✅ DNS record enumeration
- ✅ SSL/TLS certificate validation
- ✅ Public information gathering
- ❌ NO active vulnerability exploitation
- ❌ NO penetration testing
- ❌ NO brute force attacks

## Features

### 🎯 Core Capabilities

- **Typer CLI**: 5 powerful commands (scan, tui, report, self-check, doctor)
- **Textual TUI**: Interactive terminal interface
- **3 Resilient Scanners**: HTTP, DNS, SSL/TLS with graceful degradation
- **Smart Caching**: TTL-based file cache in ~/.anomradar/cache
- **Multiple Export Formats**: JSON (orjson) and HTML (Jinja2) reports
- **Global Exception Handler**: Errors logged to ~/.anomradar/last_error.json
- **Flexible Configuration**: Merge .env and anomradar.toml settings

### 🔍 Scanners

1. **HTTP Scanner**
   - Status codes and response times
   - Security headers analysis (HSTS, CSP, X-Frame-Options, etc.)
   - Redirect chain tracking
   - Server fingerprinting

2. **DNS Scanner**
   - A, AAAA, MX, TXT, NS, SOA, CNAME records
   - Multiple nameserver support
   - Graceful degradation on timeout/errors

3. **SSL/TLS Scanner**
   - Certificate validation and expiry
   - Cipher suite analysis
   - Subject Alternative Names (SAN)
   - Chain verification

### 📊 Reporting

- **JSON Export**: Fast serialization with orjson, pretty-printing
- **HTML Reports**: Professional, responsive templates with Jinja2
- **Fallback Templates**: Works even without dependencies
- **Structured Data**: Consistent format across all scanners

### 🖥️ TUI (Terminal User Interface)

- Modern, interactive interface powered by Textual
- Real-time scan execution
- Formatted results display
- Safe exception handling
- Keyboard shortcuts (q=quit, c=clear, Enter=scan)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

**One-command install (Linux/macOS):**

```bash
# Clone repository
git clone https://github.com/AnomFIN/AnomRadar.git
cd AnomRadar

# Run interactive installer
python3 scripts/asennus.py
```

**Windows:**

```cmd
REM Clone repository
git clone https://github.com/AnomFIN/AnomRadar.git
cd AnomRadar

REM Run interactive installer
scripts\asennus.bat
```

**Manual installation:**

```bash
# Install dependencies
pip install -r requirements.txt

# Create config files (optional)
cp .env.example .env
cp anomradar.toml.example anomradar.toml

# Run self-check
python -m anomradar.cli self-check
```

## Usage

### CLI Commands

```bash
# Run a scan
anomradar scan example.com

# Run specific scanners
anomradar scan example.com --scanner http --scanner dns

# Save results to file
anomradar scan example.com -o results.json

# Launch interactive TUI
anomradar tui

# Generate HTML report from scan results
anomradar report results.json -o report.html

# Run self-diagnostics
anomradar self-check

# Check for common issues
anomradar doctor

# Show version
anomradar version

# Get help
anomradar --help
```

### Python API

```python
from anomradar.core.config import Config
from anomradar.scanners import run_scan

# Load configuration
config = Config.load()

# Run all scanners
results = run_scan("example.com", config=config)

# Run specific scanner
from anomradar.scanners.http import scan_http
result = scan_http("example.com", config)

# Export results
from anomradar.exporters.json_exporter import export_json
from pathlib import Path
export_json(results, Path("results.json"))
```

## Configuration

### Environment Variables (.env)

```bash
# Application Settings
ANOMRADAR_ENV=production
ANOMRADAR_LOG_LEVEL=INFO

# Scanner Settings
ANOMRADAR_TIMEOUT=30
ANOMRADAR_MAX_RETRIES=3

# Cache Settings
ANOMRADAR_CACHE_TTL=3600
ANOMRADAR_CACHE_ENABLED=true
```

### TOML Configuration (anomradar.toml)

```toml
[application]
name = "AnomRadar"
version = "2.0.0"
environment = "production"

[logging]
level = "INFO"
format = "json"
output = "~/.anomradar/logs/anomradar.log"

[cache]
enabled = true
ttl = 3600
directory = "~/.anomradar/cache"

[scanners]
timeout = 30
max_retries = 3
user_agent = "AnomRadar/2.0 Security Scanner"
```

Configuration priority (highest to lowest):
1. Environment variables (ANOMRADAR_*)
2. TOML file settings
3. .env file settings
4. Default values

## Project Structure

```
AnomRadar/
├── anomradar/              # Main package
│   ├── cli.py             # Typer CLI with 5 commands
│   ├── core/              # Core functionality
│   ├── scanners/          # Scanner modules
│   ├── exporters/         # Export functionality
│   ├── reports/           # Report templates
│   └── tui/               # Terminal UI
├── scripts/               # Installation scripts
├── tests/                 # Test suite
├── assets/brand/          # Brand assets
├── .github/workflows/     # CI/CD
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── anomradar.toml.example # Config template
└── CHANGELOG.md          # Version history
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=anomradar
```

### Linting

```bash
# Install ruff
pip install ruff

# Run linter
ruff check anomradar/ tests/ scripts/
```

## Error Handling

AnomRadar v2 features comprehensive error handling:

- **Global Exception Handler**: All CLI commands wrapped with error handler
- **Scanner Degradation**: Scanners return structured errors instead of crashing
- **Error Logging**: Errors written to ~/.anomradar/last_error.json
- **User-Friendly Messages**: Clear error messages in console

## Security & Privacy

### Data Protection
- All scan data stored locally in ~/.anomradar/
- No external data transmission (except for scans)
- No telemetry or analytics

### Passive Scanning
- Read-only operations
- No exploits or attacks
- Respects target systems

### Responsible Use
This tool is for **authorized security assessment only**. Users must:
- Obtain proper authorization before scanning
- Comply with applicable laws and regulations
- Use the tool ethically and responsibly

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: https://github.com/AnomFIN/AnomRadar/issues
- **Discussions**: https://github.com/AnomFIN/AnomRadar/discussions

---

**AnomRadar v2 - Built with security and privacy in mind. Always scan responsibly. 🔒**
