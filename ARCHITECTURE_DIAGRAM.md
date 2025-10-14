# AnomRadar Deployment Architecture Diagram

```
                          ANOMRADAR DEPLOYMENT ARCHITECTURE
                          =================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT WORKFLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

   Local Development Machine                     anomfin.fi Server
   ════════════════════════                     ═══════════════════
   
   ┌─────────────────────┐                     ┌──────────────────────────┐
   │  Git Repository     │                     │   Web Server             │
   │  AnomRadar/         │                     │   (Apache/Nginx)         │
   │  ├── api/           │                     │                          │
   │  ├── frontend/      │─────FTP Deploy─────▶│  ┌────────────────────┐ │
   │  ├── backend/       │                     │  │  /public_html/     │ │
   │  └── deployment/    │                     │  │  ├── api/radar/    │ │
   └─────────────────────┘                     │  │  │   └── public/   │ │
                                                │  │  │       └── .php  │ │
   ┌─────────────────────┐                     │  │  └── radar-ui/     │ │
   │  deployment/        │                     │  │      ├── index.html│ │
   │  deploy-ftp.sh      │                     │  │      ├── css/      │ │
   │                     │                     │  │      └── js/       │ │
   │  Creates backup     │                     │  └────────────────────┘ │
   │  Uploads API        │                     │                          │
   │  Uploads Frontend   │                     │  ┌────────────────────┐ │
   │  Configures .env    │                     │  │  MySQL 8.0         │ │
   └─────────────────────┘                     │  │  Database:         │ │
                                                │  │  - anomradar       │ │
                                                │  │  - Tables: scans,  │ │
                                                │  │    findings, etc   │ │
                                                │  └────────────────────┘ │
                                                └──────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                            RUNTIME ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌───────────────┐
  │   End User    │
  │   Browser     │
  └───────┬───────┘
          │
          │ HTTPS
          ▼
  ┌───────────────────────────────────────────┐
  │     anomfin.fi/radar-ui                   │
  │  ┌─────────────────────────────────────┐  │
  │  │  Frontend (Static HTML/CSS/JS)      │  │
  │  │  - Search interface                 │  │
  │  │  - Reconnaissance dashboard         │  │
  │  │  - Whitelist management             │  │
  │  │  - Report viewer                    │  │
  │  └─────────────┬───────────────────────┘  │
  │                │                           │
  │                │ Fetch API                 │
  │                ▼                           │
  │  ┌─────────────────────────────────────┐  │
  │  │  PHP REST API (/api/radar/)         │  │
  │  │  - Scan CRUD operations             │  │
  │  │  - Report generation (HTML/PDF)     │  │
  │  │  - Whitelist management             │  │
  │  │  - Data purge (90-day retention)    │  │
  │  └─────────────┬───────────────────────┘  │
  │                │                           │
  │                │ PDO/mysqli                │
  │                ▼                           │
  │  ┌─────────────────────────────────────┐  │
  │  │  MySQL Database                     │  │
  │  │  - scans                            │  │
  │  │  - domains                          │  │
  │  │  - findings                         │  │
  │  │  - reports                          │  │
  │  │  - whitelist                        │  │
  │  │  - notifications                    │  │
  │  │  - audit_log                        │  │
  │  └─────────────┬───────────────────────┘  │
  └────────────────┼───────────────────────────┘
                   │
                   │ MySQL Connection
                   │ (via SSH Tunnel or Remote)
                   │
                   ▼
  ┌───────────────────────────────────────────┐
  │  Backend Scanner (Local/VPS)              │
  │  ┌─────────────────────────────────────┐  │
  │  │  Node.js + TypeScript               │  │
  │  │  ┌─────────────────────────────┐    │  │
  │  │  │  12 Scanner Modules:        │    │  │
  │  │  │  - YTJ Search               │    │  │
  │  │  │  - Domain Discovery         │    │  │
  │  │  │  - DNS Analysis             │    │  │
  │  │  │  - Email Security (SPF/DMARC)│   │  │
  │  │  │  - SSL/TLS Scanner          │    │  │
  │  │  │  - WHOIS Scanner            │    │  │
  │  │  │  - Social Media Scanner     │    │  │
  │  │  │  - Technology Scanner       │    │  │
  │  │  │  - ZAP Passive Scanning     │    │  │
  │  │  │  - Nmap Scanning            │    │  │
  │  │  │  - Contact Scraping         │    │  │
  │  │  │  - Risk Scoring             │    │  │
  │  │  └─────────────────────────────┘    │  │
  │  └─────────────────────────────────────┘  │
  └───────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW DIAGRAM                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    1. User initiates scan              2. Backend processes
       via web interface                   and stores results
    
    Browser                             Backend Scanner
       │                                     │
       │ POST /api/radar/scans              │
       │ {company: "Example Oy"}            │
       ├──────────────────────────┐         │
       │                           │         │
       ▼                           ▼         │
    PHP API                     MySQL ◄──────┤
       │                           │         │
       │ Creates scan record       │ Stores: │
       │ scan_id: 123             │ - DNS   │
       │                           │ - SPF   │
       │                           │ - SSL   │
       │                           │ - Ports │
       │                           │ - Risk  │
       │                           │         │
       │                           │         │
    3. User views results       4. Report generation
    
    Browser                             PHP API
       │                                     │
       │ GET /api/radar/scans/123           │
       ├──────────────────────────┐         │
       │                           ▼         │
       │                        MySQL        │
       │                           │         │
       │ ◄─────────────────────────┤         │
       │ Shows scan results        │         │
       │                                     │
       │ POST /api/radar/reports/123/pdf    │
       ├────────────────────────────────────▶│
       │                                     │
       │                           Generates │
       │                           PDF with  │
       │                           TCPDF     │
       │                                     │
       │ ◄────────────────────────────────────
       │ Downloads PDF report
       │


┌─────────────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT FILE STRUCTURE                               │
└─────────────────────────────────────────────────────────────────────────────┘

Local Repository                    After FTP Deployment to anomfin.fi
══════════════════                 ═══════════════════════════════════

AnomRadar/                         /public_html/
├── api/                           ├── api/radar/          (PHP API)
│   ├── public/                    │   ├── public/
│   │   ├── index.php        ────▶ │   │   ├── index.php
│   │   └── .htaccess        ────▶ │   │   └── .htaccess
│   ├── src/                 ────▶ │   ├── src/
│   ├── migrations/          ────▶ │   ├── migrations/
│   ├── composer.json        ────▶ │   ├── composer.json
│   └── .env.example               │   └── .env            (configured)
├── frontend/                      └── radar-ui/          (Frontend)
│   ├── index.html           ────▶     ├── index.html
│   ├── css/                 ────▶     ├── css/
│   └── js/                  ────▶     └── js/
├── backend/                       Not deployed (runs locally/VPS)
└── deployment/
    ├── deploy-ftp.sh        (deployment script)
    ├── setup-mysql.sh       (database helper)
    └── .env.ftp            (FTP credentials)


┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUPPORTED PLATFORMS                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  Backend Scanner Installation      Web Deployment Target
  ════════════════════════════      ════════════════════════

  ✓ Ubuntu 20.04+                   ✓ anomfin.fi (web hosting)
  ✓ Debian 11+                      ✓ Shared hosting with:
  ✓ Kali Linux 2023+                  - FTP/FTPS access
  ✓ CentOS 8+                         - MySQL 8.0+
  ✓ RHEL 8+                           - PHP 8.1+
  ✓ Fedora 36+                        - Apache/Nginx
                                      - Writable directories


┌─────────────────────────────────────────────────────────────────────────────┐
│                      SECURITY ARCHITECTURE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  1. FTP Deployment Security         2. Runtime Security
     ═══════════════════════            ══════════════════

     ┌────────────────┐                 ┌────────────────┐
     │ FTPS (SSL/TLS) │                 │ HTTPS (SSL)    │
     └────────────────┘                 └────────────────┘
            │                                   │
            ▼                                   ▼
     ┌────────────────┐                 ┌────────────────┐
     │ Credentials    │                 │ API Key Auth   │
     │ in .env.ftp    │                 │ CORS Control   │
     │ (git ignored)  │                 │ Input Sanitiz. │
     └────────────────┘                 └────────────────┘
            │                                   │
            ▼                                   ▼
     ┌────────────────┐                 ┌────────────────┐
     │ Backup before  │                 │ SQL Injection  │
     │ deployment     │                 │ Protection     │
     └────────────────┘                 └────────────────┘

  3. Database Security               4. File Security
     ═══════════════════                ═══════════════

     ┌────────────────┐                 ┌────────────────┐
     │ Strong passwd  │                 │ 755 dirs       │
     │ Limited privs  │                 │ 644 files      │
     │ SSH tunnel     │                 │ .env protected │
     └────────────────┘                 └────────────────┘
