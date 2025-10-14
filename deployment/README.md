# AnomRadar Deployment Scripts

This directory contains deployment scripts for deploying AnomRadar to anomfin.fi via FTP.

## 📁 Files

- **`.env.ftp.example`** - Template for FTP and remote MySQL configuration
- **`deploy-ftp.sh`** - Main deployment script (deploys API + Frontend)
- **`setup-mysql.sh`** - Helper script for MySQL database setup

## 🚀 Quick Start

### 1. Configure FTP Settings

```bash
# Copy template
cp .env.ftp.example .env.ftp

# Edit with your credentials
nano .env.ftp
```

### 2. Set Up MySQL Database

Choose one method:

**A) Via cPanel/phpMyAdmin (Easiest):**
1. Login to cPanel
2. Create database `anomradar`
3. Create user `anomradar`
4. Import `../api/migrations/001_initial_schema.sql`

**B) Via Helper Script:**
```bash
./setup-mysql.sh
```

### 3. Deploy to anomfin.fi

```bash
./deploy-ftp.sh
```

### 4. Post-Deployment

1. Rename `api/.env.remote` to `api/.env` on server
2. Verify file permissions (755 for dirs, 644 for files)
3. Test: https://anomfin.fi/radar-ui

## 📋 Requirements

### Local Machine
- Linux (Ubuntu, Debian, Kali, CentOS, etc.)
- `lftp` package installed
- Bash shell

Install lftp:
```bash
# Ubuntu/Debian/Kali
sudo apt-get install lftp

# CentOS/RHEL/Fedora
sudo yum install lftp
```

### Remote Server (anomfin.fi)
- FTP/FTPS access
- MySQL 8.0+
- PHP 8.1+ with extensions: mysqli, pdo, json, xml, mbstring
- Apache or Nginx with PHP-FPM

## 🔧 Configuration Reference

### FTP Settings (.env.ftp)

```bash
# FTP connection
FTP_HOST=ftp.anomfin.fi
FTP_PORT=21
FTP_USER=your_username
FTP_PASSWORD=your_password
FTP_USE_SSL=true                    # Use FTPS (recommended)

# Remote paths
FTP_REMOTE_API_PATH=/public_html/api/radar
FTP_REMOTE_FRONTEND_PATH=/public_html/radar-ui
FTP_REMOTE_REPORTS_PATH=/public_html/api/radar/reports

# MySQL on anomfin.fi
REMOTE_DB_HOST=localhost            # Usually localhost on shared hosting
REMOTE_DB_PORT=3306
REMOTE_DB_NAME=anomradar
REMOTE_DB_USER=anomradar
REMOTE_DB_PASSWORD=your_mysql_password

# URLs
REMOTE_REPORT_BASE_URL=https://anomfin.fi/api/radar/reports
REMOTE_API_BASE_URL=https://anomfin.fi/api/radar

# Backup
BACKUP_ENABLED=true
BACKUP_PATH=./backups
```

## 🌐 Deployed URLs

After deployment:

| Component | URL |
|-----------|-----|
| Frontend | https://anomfin.fi/radar-ui |
| API | https://anomfin.fi/api/radar |
| API Test | https://anomfin.fi/api/radar/scans |

## 🔄 Updating Deployment

To update an existing deployment:

```bash
# Pull latest changes
git pull origin main

# Deploy again
./deploy-ftp.sh
```

The script automatically backs up the existing deployment before updating.

## 🔐 Security Notes

- **Never commit `.env.ftp`** - contains sensitive credentials
- Use **FTPS** (FTP over SSL) - set `FTP_USE_SSL=true`
- Use **strong passwords** for MySQL and FTP
- Enable **HTTPS** on anomfin.fi
- Keep **`.env` files secure** on the server
- Set **proper file permissions** (no 777 except reports dir)

## 🐛 Troubleshooting

### FTP connection fails
```bash
# Test manually
lftp -c "open ftp://user:pass@ftp.anomfin.fi; ls; bye"

# Check credentials in .env.ftp
cat .env.ftp
```

### MySQL connection issues
- Verify database exists: Check cPanel > MySQL Databases
- Verify user has privileges
- Check credentials in api/.env on server
- Most shared hosting blocks remote MySQL (use SSH tunnel)

### Deployment incomplete
- Check lftp is installed: `which lftp`
- Verify FTP credentials
- Check remote paths exist and are writable
- Review script output for errors

### API returns 500 errors
- Check PHP error logs (cPanel > Error Log)
- Verify api/.env exists (rename from .env.remote)
- Check database connection
- Verify PHP extensions: mysqli, pdo, json, xml, mbstring

## 📚 More Information

See [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment guide.

## 🎯 Backend Scanner Connection

The backend scanner runs locally and connects to remote MySQL:

**Via SSH Tunnel (Recommended):**
```bash
# Create tunnel
ssh -L 3306:localhost:3306 user@anomfin.fi -N &

# Update backend/.env
DB_HOST=localhost
DB_PORT=3306
```

**Direct Remote (if allowed):**
```bash
# Update backend/.env
DB_HOST=anomfin.fi
DB_PORT=3306
```

Note: Most shared hosting blocks remote MySQL for security.

## ✅ Post-Deployment Checklist

- [ ] MySQL database created and migrated
- [ ] `.env.remote` renamed to `.env` on server
- [ ] File permissions set correctly (755/644)
- [ ] Frontend loads: https://anomfin.fi/radar-ui
- [ ] API responds: https://anomfin.fi/api/radar/scans
- [ ] Reports directory writable
- [ ] HTTPS enabled (SSL certificate)
- [ ] Backend scanner connected to database

---

**Ready to deploy! 🚀**
