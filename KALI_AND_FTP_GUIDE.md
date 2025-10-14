# AnomRadar - Kali Linux & FTP Deployment Guide

## 🎉 New Features

### ✅ Kali Linux Support
AnomRadar now fully supports Kali Linux installation alongside Ubuntu, Debian, CentOS, RHEL, and Fedora.

**Installation on Kali Linux:**
```bash
git clone https://github.com/AnomFIN/AnomRadar.git
cd AnomRadar
sudo chmod +x installer/install.sh
sudo installer/install.sh
```

The installer automatically detects Kali Linux and installs all required dependencies.

---

## 🌐 FTP Deployment to anomfin.fi

### Overview
AnomRadar can now be deployed to your web hosting server (anomfin.fi) via FTP with MySQL database support.

### What Gets Deployed
1. **PHP API** → `/api/radar/` on anomfin.fi
2. **Frontend (Browser GUI)** → `/radar-ui/` on anomfin.fi
3. **MySQL Database** → Used by both API and backend scanner

### Quick Deployment Steps

#### 1. Configure FTP Credentials
```bash
cd deployment
cp .env.ftp.example .env.ftp
nano .env.ftp
```

Update with your anomfin.fi credentials:
```bash
FTP_HOST=ftp.anomfin.fi
FTP_USER=your_username
FTP_PASSWORD=your_password
FTP_USE_SSL=true

REMOTE_DB_HOST=localhost
REMOTE_DB_NAME=anomradar
REMOTE_DB_USER=anomradar
REMOTE_DB_PASSWORD=your_mysql_password
```

#### 2. Set Up MySQL Database
Via cPanel or phpMyAdmin:
- Create database: `anomradar`
- Create user: `anomradar`
- Import: `api/migrations/001_initial_schema.sql`

Or use the helper script:
```bash
./deployment/setup-mysql.sh
```

#### 3. Deploy to anomfin.fi
```bash
./deployment/deploy-ftp.sh
```

#### 4. Post-Deployment
1. Rename `api/.env.remote` to `api/.env` on server (via FTP/cPanel)
2. Verify file permissions (755 for directories, 644 for files)
3. Test deployment:
   - Frontend: https://anomfin.fi/radar-ui
   - API: https://anomfin.fi/api/radar/scans

### Architecture After Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                        anomfin.fi Server                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐      ┌────────────────────────┐  │
│  │  Frontend (Browser)  │      │      PHP API           │  │
│  │  /radar-ui/          │◄─────┤  /api/radar/           │  │
│  │  - HTML/CSS/JS       │      │  - REST endpoints      │  │
│  └──────────────────────┘      │  - Report generation   │  │
│                                 └────────┬───────────────┘  │
│                                          │                   │
│                                          ▼                   │
│                                 ┌────────────────────────┐  │
│                                 │   MySQL Database       │  │
│                                 │   - Scan results       │  │
│                                 │   - Reports            │  │
│                                 │   - Whitelist          │  │
│                                 └────────┬───────────────┘  │
└─────────────────────────────────────────┼───────────────────┘
                                          │
                      ┌───────────────────┘
                      │ SSH Tunnel or Remote Connection
                      ▼
             ┌────────────────────┐
             │  Backend Scanner   │
             │  (Local/VPS)       │
             │  - Node.js         │
             │  - TypeScript      │
             │  - Scanners        │
             └────────────────────┘
```

### Backend Scanner Connection

The backend scanner runs locally or on a VPS and connects to the remote MySQL database.

**Recommended: SSH Tunnel**
```bash
# Create tunnel
ssh -L 3306:localhost:3306 user@anomfin.fi -N &

# Update backend/.env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=your_mysql_password
```

**Alternative: Direct Remote (if allowed)**
```bash
# Update backend/.env
DB_HOST=anomfin.fi
DB_PORT=3306
```

Note: Most shared hosting providers block remote MySQL connections for security.

---

## 📋 File Changes Summary

### New Files
- `DEPLOYMENT.md` - Complete deployment guide
- `deployment/.env.ftp.example` - FTP configuration template
- `deployment/deploy-ftp.sh` - Main deployment script
- `deployment/setup-mysql.sh` - MySQL setup helper
- `deployment/README.md` - Deployment scripts documentation
- `api/public/.htaccess` - Apache configuration for API routing

### Modified Files
- `installer/install.sh` - Added Kali Linux support and lftp package
- `backend/.env.example` - Added remote MySQL configuration options
- `api/.env.example` - Added FTP deployment settings
- `frontend/js/app.js` - Updated API URL detection for anomfin.fi
- `README.md` - Added deployment section and Kali Linux mention
- `installer/README.md` - Added Kali Linux to prerequisites

---

## 🚀 Features

### 1. Kali Linux Support
- ✅ Automatic detection of Kali Linux
- ✅ Install all dependencies (Node.js, PHP, MySQL, nmap, etc.)
- ✅ Compatible with Kali's package manager (apt-get)
- ✅ Same workflow as Ubuntu/Debian

### 2. FTP Deployment
- ✅ One-command deployment to anomfin.fi
- ✅ Automatic backup before deployment
- ✅ Secure FTP/FTPS support
- ✅ Deploy PHP API and Frontend simultaneously
- ✅ Automatic configuration generation

### 3. MySQL Database Integration
- ✅ Remote MySQL database on anomfin.fi
- ✅ SSH tunnel support for secure connection
- ✅ Helper script for database setup
- ✅ Automatic schema migration
- ✅ Support for both local and remote MySQL

### 4. Browser GUI on anomfin.fi
- ✅ Static HTML/CSS/JS frontend
- ✅ Automatically detects API endpoint
- ✅ Works on anomfin.fi without configuration
- ✅ Responsive design for mobile and desktop

---

## 🔧 Configuration Files

### deployment/.env.ftp
Main configuration for FTP deployment:
```bash
FTP_HOST=ftp.anomfin.fi
FTP_USER=username
FTP_PASSWORD=password
FTP_USE_SSL=true
FTP_REMOTE_API_PATH=/public_html/api/radar
FTP_REMOTE_FRONTEND_PATH=/public_html/radar-ui
REMOTE_DB_HOST=localhost
REMOTE_DB_NAME=anomradar
REMOTE_DB_USER=anomradar
REMOTE_DB_PASSWORD=password
```

### backend/.env
Backend scanner configuration (local or VPS):
```bash
# Local or tunneled MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=password

# Remote MySQL (if using SSH tunnel)
# ssh -L 3306:localhost:3306 user@anomfin.fi
```

### api/.env (on anomfin.fi server)
API configuration on remote server:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=password

REPORT_BASE_URL=https://anomfin.fi/api/radar/reports
```

---

## 🔐 Security Considerations

### FTP Security
- ✅ Use FTPS (FTP over SSL/TLS) - `FTP_USE_SSL=true`
- ✅ Never commit `.env.ftp` to Git
- ✅ Use strong passwords for FTP accounts

### MySQL Security
- ✅ Use strong database passwords
- ✅ Prefer SSH tunnels over remote MySQL connections
- ✅ Grant minimal necessary privileges
- ✅ Regular backups before deployments

### Web Server Security
- ✅ Enable HTTPS on anomfin.fi (SSL certificate)
- ✅ Proper file permissions (755/644)
- ✅ Protect `.env` files from web access
- ✅ Regular security updates

---

## 📊 URLs After Deployment

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | https://anomfin.fi/radar-ui | Browser GUI for scans |
| API Base | https://anomfin.fi/api/radar | REST API endpoint |
| List Scans | https://anomfin.fi/api/radar/scans | Get all scans |
| Reports | https://anomfin.fi/api/radar/reports | Generated reports |

---

## 🐛 Troubleshooting

### FTP Connection Issues
```bash
# Test FTP manually
lftp -c "open ftp://user:pass@ftp.anomfin.fi; ls; bye"

# Check lftp is installed
which lftp || sudo apt-get install lftp
```

### MySQL Connection Issues
```bash
# Via SSH tunnel (recommended)
ssh -L 3306:localhost:3306 user@anomfin.fi -N &

# Test connection
mysql -h localhost -u anomradar -p anomradar
```

### API 500 Errors
- Check PHP error logs in cPanel
- Verify `.env` file exists (rename from `.env.remote`)
- Test database connection via phpMyAdmin
- Check PHP extensions: mysqli, pdo, json, xml, mbstring

### Frontend Connection Failed
- Verify API URL in browser console
- Check CORS settings in `api/.env`
- Test API directly: `curl https://anomfin.fi/api/radar/scans`

---

## ✅ Post-Deployment Checklist

- [ ] MySQL database created and migrated
- [ ] `.env.remote` renamed to `.env` on server
- [ ] File permissions set (755/644)
- [ ] Frontend loads: https://anomfin.fi/radar-ui
- [ ] API responds: https://anomfin.fi/api/radar/scans
- [ ] Reports directory writable (755 or 777)
- [ ] HTTPS enabled (SSL certificate)
- [ ] Backend scanner connected via SSH tunnel
- [ ] Test scan completed successfully

---

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[deployment/README.md](deployment/README.md)** - Deployment scripts documentation
- **[README.md](README.md)** - Main project documentation
- **[HOWTO.md](HOWTO.md)** - Step-by-step setup guide

---

## 🎯 Summary

AnomRadar now supports:
1. ✅ **Kali Linux** - Full support alongside other Linux distributions
2. ✅ **FTP Deployment** - Deploy to anomfin.fi with one command
3. ✅ **Remote MySQL** - Connect backend scanner to remote database
4. ✅ **Browser GUI** - Frontend available at https://anomfin.fi/radar-ui
5. ✅ **PHP API** - Backend API at https://anomfin.fi/api/radar

**Ready to deploy! 🚀**
