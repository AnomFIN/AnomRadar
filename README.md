# AnomRadar

🔒 **Security Intelligence Platform for Company Security Assessment**

AnomRadar is a comprehensive OSINT (Open Source Intelligence) security scanning and reporting system designed to identify and report company security flaws to management. The system performs passive reconnaissance, security analysis, and risk scoring to help organizations understand their security posture.

## ⚠️ Important Notice

**AnomRadar performs only PASSIVE security scanning. No active attacks or intrusive testing are performed.**

- ✅ Passive DNS/SPF/DMARC analysis
- ✅ Public information gathering (YTJ registry, websites)
- ✅ Port/service discovery (read-only)
- ✅ OWASP ZAP passive scanning only
- ❌ NO active vulnerability exploitation
- ❌ NO penetration testing
- ❌ NO brute force attacks

## Features

### Backend Scanner (Node.js + TypeScript) - 12 Scanners
1. **YTJ Integration**: Finnish Business Registry lookups
2. **Domain Discovery**: Automatic domain identification
3. **DNS Analysis**: DNS records and security checks
4. **Email Security**: SPF/DMARC/DKIM validation
5. **ZAP Passive Scanning**: OWASP ZAP integration (passive mode only)
6. **Network Scanning**: Nmap port and service discovery
7. **Contact Scraping**: Automated contact information collection
8. **🆕 SSL/TLS Scanner**: Certificate validation, expiration, weak ciphers
9. **🆕 WHOIS Scanner**: Domain registration, expiration, privacy checks
10. **🆕 Social Media**: Presence detection on 7+ platforms
11. **🆕 Technology Stack**: CMS, frameworks, security headers detection
12. **Risk Scoring**: Algorithmic risk assessment (0-100 scale)

### PHP REST API
- **MySQL 8.0 Database**: Persistent storage for scan results
- **RESTful Endpoints**: Complete CRUD operations
- **Report Generation**: HTML and PDF reports
- **Automatic Data Purge**: 90-day retention policy
- **Whitelist Management**: Notification control (Telegram/WhatsApp)

### Static Frontend
- **Search Interface**: Initiate company security scans
- **Reconnaissance Dashboard**: View active scans and results
- **Whitelist Manager**: Configure notification recipients
- **Report Viewer**: Generate and download reports
- **Responsive Design**: Works on desktop and mobile

## Architecture

```
AnomRadar (Monorepo)
├── backend/           # Node.js + TypeScript scanner
├── api/              # PHP REST API
├── frontend/         # Static HTML/CSS/JS interface
└── installer/        # Installation scripts
```

## Quick Start

### Prerequisites
- Linux-based system (**Ubuntu, Debian, Kali Linux, CentOS, RHEL, Fedora**)
- Node.js 18+ (LTS)
- PHP 8.1+
- MySQL 8.0+
- Composer
- nmap, dig, whois utilities

### Super Easy Installation

**See [HOWTO.md](HOWTO.md) for detailed step-by-step guide with screenshots and troubleshooting!**

**Quick Install (5 minutes):**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnomFIN/AnomRadar.git
   cd AnomRadar
   ```

2. **Run the installer:**
   ```bash
   sudo chmod +x installer/install.sh
   sudo installer/install.sh
   ```

3. **Configure:**
   - Edit `backend/.env` for scanner settings
   - Edit `api/.env` for API configuration
   - Set `SIMULATION_MODE=false` for real scans (default is already false)

4. **Start services:**
   ```bash
   # Backend
   cd backend && npm start

   # Configure web server for API and frontend
   # See installer/README.md for web server configuration
   ```

For detailed installation instructions, see [installer/README.md](installer/README.md)

## Deployment to anomfin.fi

**AnomRadar can be deployed to your web server (anomfin.fi) via FTP with remote MySQL!**

### FTP Deployment Features
- 🌐 Deploy PHP API and Frontend to anomfin.fi
- 🗄️ Connect to remote MySQL database
- 📁 Automatic backup before deployment
- 🔒 Secure FTP/FTPS support
- 🚀 One-command deployment

**Quick Deployment:**
```bash
# 1. Configure FTP credentials
cd deployment
cp .env.ftp.example .env.ftp
nano .env.ftp

# 2. Set up MySQL database (via cPanel or SSH)
./setup-mysql.sh

# 3. Deploy to anomfin.fi
./deploy-ftp.sh
```

**After deployment:**
- Frontend: https://anomfin.fi/radar-ui
- API: https://anomfin.fi/api/radar

For complete deployment guide, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

## Configuration

### Backend Configuration (backend/.env)
```bash
# Database
DB_HOST=localhost
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=your_secure_password

# API Keys
YTJ_API_KEY=your_ytj_api_key
ZAP_API_KEY=your_zap_api_key

# Scanner Settings
SIMULATION_MODE=false  # OFF by default - real scans
SCAN_TIMEOUT=300000
MAX_CONCURRENT_SCANS=3

# Notifications (Whitelist Only)
NOTIFICATIONS_ENABLED=false
TELEGRAM_BOT_TOKEN=your_token
WHATSAPP_API_KEY=your_key
```

### API Configuration (api/.env)
```bash
# Database
DB_HOST=localhost
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=your_secure_password

# Data Retention
DATA_RETENTION_DAYS=90

# Reports
REPORT_OUTPUT_PATH=/var/www/anomradar/api/reports/generated

# Notifications (Whitelist Only)
NOTIFICATIONS_ENABLED=false
```

## Usage

### Web Interface

1. Open the frontend in your browser: `http://your-server/`
2. **Search Tab**: Enter company name to start a scan
3. **Reconnaissance Tab**: View active and completed scans
4. **Whitelist Tab**: Manage notification recipients
5. **Reports Tab**: Generate and download reports

### API Endpoints

```bash
# Scans
GET    /api/scans              # List all scans
GET    /api/scans/{id}         # Get scan details
POST   /api/scans              # Start new scan
DELETE /api/scans/{id}         # Delete scan

# Reports
GET    /api/reports/{scanId}                # List reports for scan
POST   /api/reports/{scanId}/html           # Generate HTML report
POST   /api/reports/{scanId}/pdf            # Generate PDF report
GET    /api/reports/{scanId}/download/{id}  # Download report

# Whitelist
GET    /api/whitelist          # List whitelist
POST   /api/whitelist          # Add to whitelist
DELETE /api/whitelist/{id}     # Remove from whitelist

# Maintenance
POST   /api/maintenance/purge  # Manual data purge (90+ days)
```

## Risk Scoring

AnomRadar calculates a risk score (0-100) based on findings:

- **0-19**: Low risk (info)
- **20-39**: Low risk
- **40-69**: Medium risk
- **70-100**: High risk

Severity weights:
- Critical: 25 points
- High: 15 points
- Medium: 8 points
- Low: 3 points
- Info: 0 points

## Security & Privacy

### Data Protection
- All scan data stored in MySQL with 90-day auto-purge
- No sensitive credentials stored in code
- Environment variables for all secrets
- API key authentication required

### Notification Whitelist
- Telegram/WhatsApp messages ONLY sent to whitelisted contacts
- No simulation messages (SIMULATION_MODE=false by default)
- Explicit opt-in required for notifications

### Passive Scanning
- No active attacks or exploits
- Read-only operations
- Respects robots.txt (where applicable)
- Minimal network impact

## Development

### Backend Development
```bash
cd backend
npm install
npm run dev        # Development mode with hot reload
npm run build      # Compile TypeScript
npm run lint       # Run ESLint
npm test          # Run tests
```

### Frontend Development
The frontend is static HTML/CSS/JS. Simply edit files and refresh browser.

## Dependencies (Pinned Versions)

All dependencies use exact versions for reproducibility:

### Backend (Node.js)
- axios: 1.6.0
- dotenv: 16.3.1
- winston: 3.11.0
- typescript: 5.2.2

### API (PHP)
- vlucas/phpdotenv: 5.5.0
- tecnickcom/tcpdf: 6.6.5

See `backend/package.json` and `api/composer.json` for complete lists.

## Project Structure

```
AnomRadar/
├── PROJECT_PLAN.md              # Complete architecture documentation
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── backend/                     # Node.js + TypeScript scanner
│   ├── src/
│   │   ├── index.ts            # Main entry point
│   │   ├── config/             # Configuration management
│   │   ├── scanners/           # Individual scanners
│   │   ├── risk-scoring/       # Risk calculation
│   │   └── utils/              # Utilities (logging, etc.)
│   ├── package.json            # Node.js dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   └── .env.example            # Environment template
├── api/                        # PHP REST API
│   ├── public/
│   │   └── index.php          # API entry point
│   ├── src/
│   │   ├── Database/          # Database connection
│   │   ├── Controllers/       # API controllers
│   │   ├── Reports/           # Report generators
│   │   └── Utils/             # Utilities
│   ├── migrations/            # Database migrations
│   ├── composer.json          # PHP dependencies
│   └── .env.example           # Environment template
├── frontend/                   # Static web interface
│   ├── index.html             # Main page
│   ├── css/
│   │   └── styles.css         # Styles
│   └── js/
│       ├── app.js             # Main application
│       ├── search.js          # Search functionality
│       ├── whitelist.js       # Whitelist management
│       └── reports.js         # Reports management
└── installer/                  # Installation tools
    ├── install.sh             # Main installer
    ├── config.template.json   # Config template
    └── README.md              # Installation guide
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

This tool is for **authorized security assessment only**. Users are responsible for:
- Obtaining proper authorization before scanning
- Complying with applicable laws and regulations
- Using the tool ethically and responsibly
- Not using for malicious purposes

The authors are not responsible for misuse of this tool.

## Support

- **Documentation**: See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed architecture
- **Installation Help**: See [installer/README.md](installer/README.md)
- **Issues**: https://github.com/AnomFIN/AnomRadar/issues

---

**Built with security and privacy in mind. Always scan responsibly. 🔒**
