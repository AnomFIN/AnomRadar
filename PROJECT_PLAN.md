# AnomRadar - Project Plan

## Overview
AnomRadar is a comprehensive OSINT (Open Source Intelligence) security scanning and reporting system designed to identify and report company security flaws to management. The system is built as a monorepo with three main components working together.

## Architecture

### 1. Backend Scanner (Node.js + TypeScript)
**Purpose**: Passive OSINT scanning engine that collects security intelligence

**Key Features - 12 Scanner Modules**:
1. **YTJ (Finnish Business Registry) Search**: Initial company lookup and data gathering
2. **Domain Discovery**: Automated domain identification from company data
3. **DNS Analysis**: DNS record validation and security checks
4. **SPF/DMARC Checks**: Email security policy verification
5. **ZAP Passive Scanning**: OWASP ZAP passive security scanning (no active attacks)
6. **Nmap Scanning**: Network port and service discovery
7. **Contact Scraping**: Automated collection of contact information
8. **🆕 SSL/TLS Certificate Scanner**: Certificate validity, expiration, weak cipher detection
9. **🆕 WHOIS Scanner**: Domain registration info, expiration dates, privacy protection
10. **🆕 Social Media Scanner**: Presence detection across 7+ platforms (LinkedIn, Twitter, Facebook, Instagram, YouTube, TikTok, GitHub)
11. **🆕 Technology Stack Scanner**: Identifies 30+ technologies (WordPress, React, PHP, etc.), security headers, debug mode
12. **Risk Score Calculation**: Algorithmic risk assessment based on findings

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
=======
# 📡 AnomRadar – Full Project Plan

## 🧠 Vision

**AnomRadar** on autonominen OSINT- ja tietoturvaskannerialusta, joka kerää, analysoi ja raportoi julkisesti saatavaa yritystietoa yhdestä hakukentästä. Sen tarkoitus on antaa yrityksille kokonaisvaltainen näkyvyys heidän ulkoiseen hyökkäyspintaansa: mitä tietoa yrityksestä löytyy netistä, mitä voidaan päätellä, mitkä hyökkäyspolut ovat mahdollisia — ja miten riskejä voidaan vähentää ennen kuin joku muu hyödyntää niitä.

Tavoite: Rakentaa **täysin automaattinen ja laajennettava järjestelmä**, joka tekee tietoturvatestaajan tai OSINT-asiantuntijan työn 24/7 – ilman että kukaan klikkaa nappia.

---

## 📍 Kokonaisarkkitehtuuri

### 1. Backend (Node.js + TypeScript)
- Asennetaan **kotipalvelimelle** tai VPS:lle.
- Palvelu toimii Cloudflare Tunnelin kautta julkisessa osoitteessa `https://copilot.anomfin.fi`.
- Vastaa koko tiedonkeruuprosessin orkestroinnista ja analyysistä.

### 2. REST API (PHP + MySQL)
- Hostataan `anomfin.fi` webhotellissa polussa `/api/radar/`.
- Vastaanottaa backendin lähettämän datan ja tallentaa sen **MySQL 8.0** -tietokantaan.
- Luo ja palvelee **HTML- ja PDF-raportteja** sekä teknisiä Markdown-liitteitä.
- Vastaa tietojen säilytys- ja poistopolitiikasta (90 päivän automaattinen poisto).

### 3. Frontend (Static UI)
- Kevyt käyttöliittymä, hostattu `anomfin.fi` alla esim. `/radar-ui/`.
- Käyttöliittymä tarjoaa:
  - Yrityshaun (nimi tai Y-tunnus) PRH/YTJ:n avoimesta rajapinnasta.
  - Rekonisivun, jossa näkyy työn eteneminen ja löydökset.
  - Whitelist-hyväksynnän Telegram- ja WhatsApp-simulaatioita varten.
  - Raporttisivun, josta voi ladata johtotason raportit ja tekniset liitteet.

---

## 🧰 Tietovirta – “Data seuraa dataa”

1. **Syöte:** Käyttäjä antaa yrityksen nimen tai Y-tunnuksen.
2. **PRH/YTJ-integraatio:** Backend hakee yrityksen perustiedot (nimi, y-tunnus, muoto, rekisteröintipäivä jne.).
3. **Domain discovery:** Yrityksen nimen perusteella haetaan ja validoidaan todennäköiset domainit.
4. **DNS- ja sähköpostianalyysi:** SPF-, DKIM- ja DMARC-tietueet, MX-palvelimet, riskitasot.
5. **Verkkopalvelinskanneeraus:** OWASP ZAPin passiivinen analyysi, sivuston rakenteen ja haavoittuvuuksien tunnistus.
6. **Porttiskannaus:** Nmap tarkistaa top-100 portit ja avoimet palvelut.
7. **Yhteystietojen haku:** Sivustolta ja muista julkisista lähteistä kerätään puhelinnumeroita ja sähköpostiosoitteita (robots.txt huomioiden).
8. **Vuototarkistukset:** Valinnaisesti tarkistetaan HIBP-rajapinnan kautta, onko tunnistetietoja vuotanut.
9. **Riskimallinnus:** Kaikki löydökset pisteytetään ja luokitellaan (Low / Medium / High).
10. **Raportointi:** Luodaan Executive PDF, HTML-yhteenveto ja tekninen Markdown-liite.

---

## 🛠️ Tekninen stack

| Komponentti | Teknologia |
|------------|------------|
| Backend | Node.js 20+, TypeScript, Express |
| Data-keruu | DNS (node:dns), Axios/Undici, OWASP ZAP API, Nmap |
| API | PHP 8.3, mysqli, JWT/Bearer + Cloudflare IP-rajaus |
| DB | MySQL 8.0 (utf8mb4), indeksoitu schema |
| UI | HTML5, Tailwind, Vanilla JS |
| Simulaatiot | Telegram Bot API, WhatsApp Cloud API |
| Click tracking | PHP (GET-logger + MySQL) |
| Infra | Cloudflare Tunnel, PM2, cron |

---

## 📊 Tietokantarakenne (pääkohdat)

- `companies`: yrityksen perustiedot
- `domains`: löydetyt domainit ja lähteet
- `scans`: rekonstrun statukset, riskipisteet ja metadata
- `email_auth`: SPF/DKIM/DMARC tulokset ja riskit
- `web_alerts`: ZAPin löytämät High/Medium-riskit
- `ports`: avoimet portit ja palvelut
- `contacts`: löydetyt puhelinnumerot ja sähköpostit (whitelist-info mukana)
- `leaks`: HIBP/vuotojen tulokset
- `reports`: raporttitiedostojen sijainnit ja URL:t

---

## 📡 Simulaatiot ja eettiset rajat

- Oletuksena `simulation_enabled: false`: ei viestien lähetyksiä ennen kuin käyttäjä hyväksyy ne UI:ssa.
- Viestit lähetetään vain **whitelistatuiksi merkityille kontakteille**.
- Klikkilinkit ohjataan `https://test.anomfin.fi` -sandboxiin, joka kirjaa klikkaukset MySQL:ään.
- Robots.txt noudatetaan aina.  
- Kaikki data salataan siirrossa ja PII tallennetaan minimitasolla.

---

## 📈 Riskipisteytys (0–100)

| Tarkistus | Painoarvo |
|----------|-----------|
| DMARC puuttuu | +25 |
| DMARC p=none | +15 |
| SPF puuttuu | +10 |
| Web High riskit | +5 per alert (max +25) |
| Web Medium riskit | +2 per alert (max +10) |
| Avoimet hallintaportit | max +20 |
| HIBP osumat | +10 |
| SMS riskit (Medium/High) | +5 / +10 |

Luokitus:  
- **0–30:** Low  
- **31–60:** Medium  
- **61–100:** High

---

## 📅 Tiekartta

### 🥇 Vaihe 1 – MVP (v1.0)
- PRH/YTJ-haku ja domain discovery
- DNS/SPF/DMARC analyysi
- ZAP-passive & Nmap top-100
- Tietokantamalli ja API
- Executive-raportti (HTML/PDF)

### 🥈 Vaihe 2 – Enrichment (v1.1)
- Contact discovery + vuototarkistus
- HIBP-integraatio
- Riskimallin viimeistely
- Tekninen Markdown-liite

### 🥉 Vaihe 3 – Simulaatiot (v1.2)
- Telegram/WhatsApp whitelist-skenaariot
- Klikkiseuranta sandbox-domainissa
- UI-pohjainen whitelist-hallinta

### 🏁 Vaihe 4 – Automaatio & integraatiot (v1.3+)
- Jatkuva skannaus / ajastukset
- Jira / Slack / Teams -integraatiot
- Multi-domain scanning ja organisaatiotasoinen raportointi
- API-tuki kolmannen osapuolen SIEM/SOC -järjestelmille

---

## 🧱 Turva ja tietosuoja

- **90 päivän poistopolitiikka:** kaikki löydökset, kontaktit ja raportit poistetaan automaattisesti.  
- **Audit-trail:** jokainen pyyntö, skannaus ja raportti kirjataan.  
- **Ei aktiivisia hyökkäyksiä:** vain passiivinen tiedonkeruu ja analyysi.  
- **Lakisääteinen käyttö:** tarkoitettu vain luvalliseen tietoturvatestaamiseen ja omaisuuden suojaukseen.

---

## ✅ Menestysmittarit

- ⏱️ Täydellinen rekoni alle 10 minuutissa.  
- 📊 Riskipisteiden tarkkuus ±5 pisteen sisällä manuaalisesta auditoinnista.  
- 📁 Raportti valmis PDF/HTML-muodossa automaattisesti ilman manuaalista työtä.  
- 📬 100 % viesteistä menee vain whitelistatuiksi merkityille vastaanottajille.  
- 🔁 Päivitykset CI/CD-putkessa alle 5 minuutissa.

---

## 📌 Yhteenveto

**AnomRadar** ei ole yksittäinen työkalu — se on täysi **OSINT-, recon- ja tietoturva-analyysialusta**, joka automatisoi koko prosessin yrityksen julkisen hyökkäyspinnan kartoittamisesta selkeään toimitusjohtajalle tarkoitettuun raporttiin asti. Sen arvo on siinä, että se havaitsee ja esittää *kaiken, minkä hyökkääjä voisi löytää* — mutta ennen kuin kukaan muu tekee sen.
