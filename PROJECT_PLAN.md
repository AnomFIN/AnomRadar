# AnomRadar - Project Plan

## Overview
AnomRadar is a comprehensive OSINT (Open Source Intelligence) security scanning and reporting system designed to identify and report company security flaws to management. The system is built as a monorepo with three main components working together.

## Architecture

### 1. Backend Scanner (Node.js + TypeScript)
**Purpose**: Passive OSINT scanning engine that collects security intelligence

**Key Features**:
- **YTJ (Finnish Business Registry) Search**: Initial company lookup and data gathering
- **Domain Discovery**: Automated domain identification from company data
- **DNS Analysis**: DNS record validation and security checks
- **SPF/DMARC Checks**: Email security policy verification
- **ZAP Passive Scanning**: OWASP ZAP passive security scanning (no active attacks)
- **Nmap Scanning**: Network port and service discovery
- **Contact Scraping**: Automated collection of contact information
- **Risk Score Calculation**: Algorithmic risk assessment based on findings

**Technology Stack**:
- Node.js 18+ (LTS)
- TypeScript 5.x
- Pinned dependencies for stability

**Configuration**:
- API tokens (YTJ, ZAP, etc.)
- Scanner settings
- Risk scoring thresholds
- Simulation mode OFF by default (only real scans)

### 2. PHP REST API
**Purpose**: Data persistence, report generation, and API interface

**Key Features**:
- **MySQL 8.0 Database**: Store scan results and metadata
- **RESTful API**: CRUD operations for scans, results, and reports
- **HTML Report Generation**: Web-based reports
- **PDF Report Generation**: Downloadable PDF reports
- **90-Day Data Purge**: Automatic cleanup of old scan data
- **Whitelist Management**: Telegram/WhatsApp message filtering (only whitelist notifications enabled)

**Technology Stack**:
- PHP 8.1+
- MySQL 8.0
- Composer for dependency management
- PDF generation library (e.g., TCPDF or Dompdf)

**API Endpoints**:
- `/api/scans` - Scan management
- `/api/results` - Result retrieval
- `/api/reports` - Report generation
- `/api/whitelist` - Whitelist management
- `/api/notifications` - Notification settings

### 3. Static Frontend
**Purpose**: User interface for system interaction

**Key Features**:
- **Search Interface**: Company/domain search functionality
- **Reconnaissance Dashboard**: View scan progress and results
- **Whitelist Management**: Configure allowed domains and contacts
- **Report Viewer**: Display and download reports
- **Responsive Design**: Mobile and desktop compatibility

**Technology Stack**:
- HTML5, CSS3, JavaScript (ES6+)
- Static files (no framework dependencies initially)
- Fetch API for REST calls

## Monorepo Structure
```
AnomRadar/
├── README.md
├── PROJECT_PLAN.md
├── .gitignore
├── docker-compose.yml          # Optional: For local development
├── installer/                  # Installation and configuration scripts
│   ├── install.sh
│   ├── config.template.json
│   └── README.md
├── backend/                    # Node.js + TypeScript scanner
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── .env.example
│   ├── src/
│   │   ├── index.ts
│   │   ├── config/
│   │   ├── scanners/
│   │   │   ├── ytj.ts
│   │   │   ├── domain.ts
│   │   │   ├── dns.ts
│   │   │   ├── spf-dmarc.ts
│   │   │   ├── zap.ts
│   │   │   ├── nmap.ts
│   │   │   └── contact-scraper.ts
│   │   ├── risk-scoring/
│   │   └── utils/
│   └── dist/                   # Compiled TypeScript output
├── api/                        # PHP REST API
│   ├── composer.json
│   ├── composer.lock
│   ├── .env.example
│   ├── public/
│   │   └── index.php
│   ├── src/
│   │   ├── Database/
│   │   ├── Controllers/
│   │   ├── Models/
│   │   ├── Reports/
│   │   └── Utils/
│   ├── migrations/
│   └── config/
└── frontend/                   # Static web interface
    ├── index.html
    ├── css/
    │   └── styles.css
    ├── js/
    │   ├── app.js
    │   ├── search.js
    │   ├── whitelist.js
    │   └── reports.js
    └── assets/
```

## Security & Privacy Considerations
1. **Passive Scanning Only**: No active attacks or intrusive testing
2. **Simulation Mode**: Disabled by default (must be explicitly enabled)
3. **Whitelist-Only Notifications**: TG/WhatsApp messages only for whitelisted contacts
4. **Data Retention**: 90-day automatic purge
5. **API Authentication**: Token-based security
6. **Input Validation**: All user inputs sanitized
7. **Secrets Management**: Environment variables, never in code

## Installation Process
1. Run installer script
2. Configure API tokens and URLs
3. Set up MySQL database
4. Initialize backend service
5. Configure PHP API
6. Deploy static frontend

## Dependencies (Pinned Versions)
All dependencies will use exact versions (not ranges) to ensure reproducibility.

## Notification System
- **Telegram/WhatsApp Integration**: Opt-in, whitelist-only
- **No Simulation Messages**: Only real scan results sent
- **Configurable Thresholds**: Admin-defined notification triggers

## Report Generation
- **HTML Format**: Interactive web reports
- **PDF Format**: Downloadable archive reports
- **Scheduled Reports**: Daily/weekly summaries
- **On-Demand Reports**: Single scan reports

## Data Purge Policy
- Scans older than 90 days automatically deleted
- Configurable retention period
- Archive option for critical findings

## Development Phases
1. **Phase 1**: Project structure and configuration
2. **Phase 2**: Backend scanner implementation
3. **Phase 3**: PHP API and database
4. **Phase 4**: Frontend interface
5. **Phase 5**: Integration and testing
6. **Phase 6**: Documentation and deployment

## Testing Strategy
- Unit tests for critical functions
- Integration tests for API endpoints
- End-to-end tests for full scan workflow
- Security testing for vulnerabilities

## Deployment
- Docker support for containerization
- Systemd services for production
- Environment-based configuration
- Health check endpoints

## Future Enhancements
- Additional OSINT sources
- Machine learning risk scoring
- Multi-language support
- Advanced reporting analytics
- Real-time monitoring dashboard
