# AnomRadar Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AnomRadar System                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│                  │         │                  │         │                  │
│    Frontend      │◄────────│    PHP API       │◄────────│    Backend       │
│  (HTML/CSS/JS)   │  HTTP   │  (REST/MySQL)    │  Store  │  (Node.js/TS)    │
│                  │         │                  │         │                  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
        │                            │                            │
        │                            │                            │
        ▼                            ▼                            ▼
   User Actions              Database Layer               External Services
                                                                   │
                                                    ┌──────────────┼──────────────┐
                                                    │              │              │
                                                    ▼              ▼              ▼
                                                  YTJ API      OWASP ZAP      Network
                                                  (Finnish)    (Security)     (DNS/Nmap)
```

## Component Details

### Frontend (Static)
```
┌─────────────────────────────────────────┐
│           User Interface                │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │ Search  │  │  Recon  │  │Whitelist││
│  └─────────┘  └─────────┘  └─────────┘│
│                                         │
│  ┌─────────────────────────────────┐   │
│  │        Reports                  │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
         │
         │ Fetch API
         ▼
┌─────────────────────────────────────────┐
│           REST API                      │
└─────────────────────────────────────────┘
```

### PHP REST API
```
┌─────────────────────────────────────────┐
│         API Entry Point                 │
│         (public/index.php)              │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │  Router      │  │  Response    │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Controllers                │  │
│  │  • ScanController               │  │
│  │  • ReportController             │  │
│  │  • WhitelistController          │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       Report Generators          │  │
│  │  • HtmlReportGenerator          │  │
│  │  • PdfReportGenerator (TCPDF)   │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
         │
         │ PDO
         ▼
┌─────────────────────────────────────────┐
│         MySQL 8.0 Database              │
│  • scans                                │
│  • domains                              │
│  • findings                             │
│  • reports                              │
│  • whitelist                            │
│  • notifications                        │
│  • audit_log                            │
└─────────────────────────────────────────┘
```

### Backend Scanner (Node.js)
```
┌─────────────────────────────────────────┐
│        Main Entry (index.ts)            │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Scanner Orchestrator           │  │
│  │   (Coordinates all scanners)     │  │
│  └──────────────────────────────────┘  │
│         │                               │
│         ▼                               │
│  ┌──────────────────────────────────┐  │
│  │   Scanner Modules                │  │
│  │   1. YTJ Scanner                 │  │
│  │   2. Domain Scanner              │  │
│  │   3. DNS Scanner                 │  │
│  │   4. SPF/DMARC Scanner           │  │
│  │   5. ZAP Scanner (passive)       │  │
│  │   6. Nmap Scanner                │  │
│  │   7. Contact Scraper             │  │
│  └──────────────────────────────────┘  │
│         │                               │
│         ▼                               │
│  ┌──────────────────────────────────┐  │
│  │   Risk Scorer                    │  │
│  │   • Calculate score (0-100)      │  │
│  │   • Assign risk level            │  │
│  │   • Prioritize findings          │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

## Data Flow

### Scan Workflow
```
1. User Input (Company Name)
        │
        ▼
2. Frontend → POST /api/scans
        │
        ▼
3. API → Create Scan Record (status: pending)
        │
        ▼
4. Backend → Scan Orchestrator
        │
        ├─> YTJ Lookup
        │   └─> Extract domains
        │
        ├─> Domain Discovery
        │   └─> Find additional domains
        │
        ├─> For each domain:
        │   ├─> DNS Analysis
        │   ├─> SPF/DMARC Check
        │   ├─> ZAP Passive Scan
        │   ├─> Nmap Port Scan
        │   └─> Contact Scraping
        │
        ▼
5. Risk Scoring
        │
        ▼
6. Store Results in Database
        │
        ▼
7. Update Scan Status (status: completed)
        │
        ▼
8. (Optional) Send Notifications
        │   (Only to whitelisted contacts)
        │
        ▼
9. User Views Results
        │
        ▼
10. Generate Reports (HTML/PDF)
```

### Report Generation Flow
```
1. User Request (Scan ID)
        │
        ▼
2. Frontend → POST /api/reports/{scanId}/pdf
        │
        ▼
3. API → Fetch Scan Data from DB
        │
        ▼
4. Report Generator
        │   • Load scan details
        │   • Load findings
        │   • Format content
        │   • Generate PDF (TCPDF)
        │
        ▼
5. Save Report File
        │
        ▼
6. Store Report Metadata in DB
        │
        ▼
7. Return Download URL
        │
        ▼
8. User Downloads Report
```

## Security Architecture

### Passive Scanning Only
```
┌─────────────────────────────────────────┐
│        External Services                │
├─────────────────────────────────────────┤
│                                         │
│  ✅ Read-only Operations                │
│  ✅ Public Information Only             │
│  ✅ No Active Attacks                   │
│  ✅ No Exploitation                     │
│                                         │
│  Allowed:                               │
│  • DNS queries (dig)                    │
│  • Port scanning (nmap -sV)            │
│  • HTTP GET requests                    │
│  • ZAP passive spider                   │
│  • Public registry lookups              │
│                                         │
│  Not Allowed:                           │
│  • SQL injection attempts               │
│  • XSS payloads                         │
│  • Brute force attacks                  │
│  • Buffer overflows                     │
│  • DoS attacks                          │
│                                         │
└─────────────────────────────────────────┘
```

### Notification Whitelist
```
┌─────────────────────────────────────────┐
│     Notification System                 │
├─────────────────────────────────────────┤
│                                         │
│  Scan Complete                          │
│       │                                 │
│       ▼                                 │
│  Check Whitelist                        │
│       │                                 │
│       ├─> Telegram Chat IDs             │
│       │   (Only whitelisted)            │
│       │                                 │
│       └─> WhatsApp Numbers              │
│           (Only whitelisted)            │
│                                         │
│  ❌ No simulation messages              │
│  ❌ No unauthorized recipients          │
│  ✅ Explicit opt-in required            │
│                                         │
└─────────────────────────────────────────┘
```

## Database Schema

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   scans      │────<│   domains    │     │  findings    │
│              │  1:N│              │     │              │
│ • id         │     │ • id         │     │ • id         │
│ • scan_id    │     │ • scan_id    │     │ • scan_id    │
│ • company    │     │ • domain     │     │ • type       │
│ • risk_score │     └──────────────┘     │ • severity   │
│ • risk_level │                          │ • title      │
│ • status     │                          │ • description│
└──────────────┘                          │ • evidence   │
      │                                   └──────────────┘
      │ 1:N
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   reports    │     │  whitelist   │     │ notifications│
│              │     │              │     │              │
│ • id         │     │ • id         │     │ • id         │
│ • scan_id    │     │ • entity_type│     │ • scan_id    │
│ • type       │     │ • entity_val │     │ • type       │
│ • file_path  │     │ • description│     │ • recipient  │
└──────────────┘     └──────────────┘     │ • status     │
                                           └──────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Production Server                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Web Server (Nginx/Apache)              │    │
│  │  • Serve static frontend                       │    │
│  │  • Proxy API requests to PHP-FPM               │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         PHP-FPM                                │    │
│  │  • Execute PHP API                             │    │
│  │  • Generate reports                            │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Node.js Backend (Systemd)              │    │
│  │  • Run scanners                                │    │
│  │  • Process scan queue                          │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         MySQL 8.0                              │    │
│  │  • Store scan results                          │    │
│  │  • Manage whitelist                            │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Cron Jobs                              │    │
│  │  • 90-day data purge (daily)                   │    │
│  │  • Log rotation                                │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Performance Considerations

### Scan Concurrency
```
┌─────────────────────────────────────────┐
│   Scan Queue                            │
│                                         │
│   Max 3 concurrent scans                │
│   (Configurable)                        │
│                                         │
│   ┌─────┐  ┌─────┐  ┌─────┐           │
│   │Scan1│  │Scan2│  │Scan3│           │
│   └─────┘  └─────┘  └─────┘           │
│      ↓        ↓        ↓               │
│   Running  Running  Running            │
│                                         │
│   ┌─────┐  ┌─────┐                    │
│   │Scan4│  │Scan5│  ...               │
│   └─────┘  └─────┘                    │
│   Pending  Pending                     │
│                                         │
└─────────────────────────────────────────┘
```

### Data Retention
```
┌─────────────────────────────────────────┐
│   Data Lifecycle                        │
│                                         │
│   Day 0:  Scan created                  │
│   Day 1-89: Available                   │
│   Day 90: Auto-purged                   │
│                                         │
│   Cron: Daily at 2:00 AM                │
│   curl -X POST /api/maintenance/purge   │
│                                         │
└─────────────────────────────────────────┘
```

## Error Handling

```
┌─────────────────────────────────────────┐
│   Error Flow                            │
│                                         │
│   Scanner Error                         │
│        │                                │
│        ├─> Log to file                  │
│        ├─> Continue with next scanner   │
│        └─> Include in findings          │
│                                         │
│   API Error                             │
│        │                                │
│        ├─> Return JSON error            │
│        ├─> Log to file                  │
│        └─> HTTP status code             │
│                                         │
│   Database Error                        │
│        │                                │
│        ├─> Rollback transaction         │
│        ├─> Log to file                  │
│        └─> Return 500 error             │
│                                         │
└─────────────────────────────────────────┘
```

---

**Last Updated:** 2025-10-01  
**Version:** 1.0.0  
**Architecture:** Monorepo with 3 components
