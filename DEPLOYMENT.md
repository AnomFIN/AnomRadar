# AnomRadar Deployment Guide

This guide covers deploying AnomRadar to anomfin.fi via FTP with remote MySQL database.

## 📋 Prerequisites

### Local System Requirements
- Linux system (Ubuntu, Debian, **Kali Linux**, CentOS, RHEL, Fedora)
- `lftp` installed for FTP deployment
- Git for repository access
- Bash shell

### Remote Server Requirements (anomfin.fi)
- **Web hosting with FTP access**
- **MySQL 8.0+ database**
- **PHP 8.1+ with extensions**: mysqli, pdo, json, xml, mbstring
- **Web server**: Apache or Nginx with PHP-FPM
- **Writable directories** for reports and logs

---

## 🚀 Quick Deployment

### Step 1: Configure FTP Credentials

1. **Copy the FTP configuration template:**
   ```bash
   cd deployment
   cp .env.ftp.example .env.ftp
   ```

2. **Edit `.env.ftp` with your anomfin.fi credentials:**
   ```bash
   nano .env.ftp
   ```

   Update these values:
   ```bash
   FTP_HOST=ftp.anomfin.fi
   FTP_USER=your_ftp_username
   FTP_PASSWORD=your_ftp_password
   FTP_USE_SSL=true
   
   # Remote paths on your server
   FTP_REMOTE_API_PATH=/public_html/api/radar
   FTP_REMOTE_FRONTEND_PATH=/public_html/radar-ui
   
   # MySQL credentials on anomfin.fi
   REMOTE_DB_HOST=localhost
   REMOTE_DB_NAME=anomradar
   REMOTE_DB_USER=anomradar
   REMOTE_DB_PASSWORD=your_secure_mysql_password
   ```

### Step 2: Set Up MySQL Database

**Option A: Via cPanel/phpMyAdmin (Recommended)**
1. Login to your hosting control panel (cPanel)
2. Open MySQL Databases or phpMyAdmin
3. Create database: `anomradar`
4. Create user: `anomradar` with a secure password
5. Grant all privileges on `anomradar.*` to user `anomradar`
6. Import schema: Upload and execute `api/migrations/001_initial_schema.sql`

**Option B: Via SSH (if available)**
```bash
# Run the MySQL setup helper script
./deployment/setup-mysql.sh
```

This will guide you through the setup and provide SQL commands to run.

**Option C: Manual SQL Commands**
```sql
-- Connect to MySQL
mysql -u root -p

-- Create database and user
CREATE DATABASE IF NOT EXISTS anomradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'anomradar'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON anomradar.* TO 'anomradar'@'localhost';
FLUSH PRIVILEGES;
EXIT;

-- Import schema
mysql -u anomradar -p anomradar < api/migrations/001_initial_schema.sql
```

### Step 3: Deploy to anomfin.fi

Run the deployment script:
```bash
./deployment/deploy-ftp.sh
```

This will:
- ✅ Create a backup of existing deployment (if any)
- ✅ Deploy PHP API to `/api/radar/`
- ✅ Deploy Frontend (Browser GUI) to `/radar-ui/`
- ✅ Create necessary directories
- ✅ Generate remote `.env` configuration

### Step 4: Post-Deployment Configuration

1. **Rename environment file:**
   - Via FTP client or cPanel File Manager
   - Navigate to `/api/radar/`
   - Rename `.env.remote` to `.env`

2. **Verify file permissions:**
   - Directories: `755` (rwxr-xr-x)
   - Files: `644` (rw-r--r--)
   - Reports directory: `777` or `755` with www-data ownership

3. **Test the deployment:**
   - Frontend: https://anomfin.fi/radar-ui
   - API: https://anomfin.fi/api/radar/scans

### Step 5: Configure Backend Scanner

The backend scanner can run on your local machine or a VPS and connect to the remote MySQL database.

**Option A: SSH Tunnel (Recommended)**
```bash
# Create SSH tunnel to MySQL on anomfin.fi
ssh -L 3306:localhost:3306 user@anomfin.fi -N &

# Update backend/.env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=your_mysql_password
```

**Option B: Remote MySQL (if allowed)**
```bash
# Update backend/.env for direct remote connection
DB_HOST=anomfin.fi
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=your_mysql_password
```

**Note:** Most shared hosting providers don't allow remote MySQL connections for security. Use SSH tunnel instead.

---

## 📁 Deployment Structure

After deployment, your anomfin.fi server will have:

```
/public_html/
├── api/
│   └── radar/                    # PHP API
│       ├── public/
│       │   └── index.php        # API entry point
│       ├── src/                 # API source code
│       ├── migrations/          # Database migrations
│       ├── .env                 # Configuration (from .env.remote)
│       ├── composer.json
│       └── reports/
│           └── generated/       # Generated reports
└── radar-ui/                    # Frontend (Browser GUI)
    ├── index.html
    ├── css/
    │   └── styles.css
    └── js/
        ├── app.js
        ├── search.js
        ├── whitelist.js
        └── reports.js
```

---

## 🌐 Web Server Configuration

### Apache (.htaccess)

The API includes a `.htaccess` file for Apache. Ensure `mod_rewrite` is enabled:

```apache
# /public_html/api/radar/public/.htaccess
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.php [QSA,L]
</IfModule>
```

### Nginx (if applicable)

If your host uses Nginx, add this to your server configuration:

```nginx
server {
    listen 80;
    server_name anomfin.fi www.anomfin.fi;
    
    # Frontend
    location /radar-ui {
        root /public_html;
        index index.html;
        try_files $uri $uri/ /radar-ui/index.html;
    }
    
    # API
    location /api/radar {
        root /public_html/api/radar/public;
        try_files $uri /index.php?$args;
        
        location ~ \.php$ {
            include fastcgi_params;
            fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        }
    }
    
    # Reports
    location /api/radar/reports {
        root /public_html/api/radar;
        autoindex off;
    }
}
```

---

## 🔄 Updating the Deployment

To update your deployment with new changes:

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Run deployment again:**
   ```bash
   ./deployment/deploy-ftp.sh
   ```

The script will automatically backup the existing deployment before updating.

---

## 🗄️ Database Management

### Backup Database
```bash
# Via SSH
mysqldump -u anomradar -p anomradar > anomradar-backup-$(date +%Y%m%d).sql

# Via phpMyAdmin
# Export > Custom > Save to file
```

### Restore Database
```bash
# Via SSH
mysql -u anomradar -p anomradar < anomradar-backup.sql

# Via phpMyAdmin
# Import > Choose file > Go
```

### Data Retention
The system automatically purges scan data older than 90 days. Configure in `api/.env`:
```bash
DATA_RETENTION_DAYS=90
```

---

## 🔐 Security Checklist

- [ ] Use strong, unique passwords for MySQL
- [ ] Use FTPS (FTP over SSL/TLS) - set `FTP_USE_SSL=true`
- [ ] Enable HTTPS on anomfin.fi (SSL certificate)
- [ ] Set proper file permissions (no 777 except reports directory)
- [ ] Keep `.env` files secure and never commit to Git
- [ ] Regularly update PHP and MySQL
- [ ] Enable CORS only for trusted domains
- [ ] Use API key authentication (`API_KEY` in api/.env)
- [ ] Monitor logs regularly

---

## 🐛 Troubleshooting

### Issue: FTP connection fails
**Solution:**
```bash
# Test FTP connection manually
lftp -c "open ftp://your_user:your_pass@ftp.anomfin.fi; ls; bye"

# Check .env.ftp settings
cat deployment/.env.ftp

# Verify credentials with your hosting provider
```

### Issue: API returns 500 errors
**Solution:**
```bash
# Check PHP error logs (via cPanel or SSH)
tail -f /path/to/php-errors.log

# Verify .env file exists and has correct permissions
# Via FTP: api/radar/.env should exist (renamed from .env.remote)

# Check database connection
# Test from phpMyAdmin or command line
```

### Issue: Database connection failed
**Solution:**
```bash
# Verify MySQL credentials in api/.env
# Ensure database exists and user has privileges
# Check if remote MySQL connections are allowed (usually disabled on shared hosting)
```

### Issue: Frontend shows "API connection failed"
**Solution:**
```bash
# Check CORS settings in api/.env
CORS_ALLOWED_ORIGINS=https://anomfin.fi,https://www.anomfin.fi

# Verify API URL in frontend/js/app.js
# Should be: /api/radar or https://anomfin.fi/api/radar

# Test API directly:
curl https://anomfin.fi/api/radar/scans
```

### Issue: Reports not generating
**Solution:**
```bash
# Check reports directory exists and is writable
# Via FTP: /api/radar/reports/generated should exist with 755 or 777 permissions

# Verify TCPDF is installed
# In api/: composer install

# Check PHP memory limit and max execution time
# In php.ini or .user.ini:
memory_limit = 256M
max_execution_time = 300
```

---

## 📊 Monitoring Deployment

### Check API Status
```bash
curl https://anomfin.fi/api/radar/scans
```

Expected response:
```json
{
  "status": "success",
  "data": [],
  "message": "Scans retrieved successfully"
}
```

### Check Frontend
Visit: https://anomfin.fi/radar-ui

You should see:
- Search tab for initiating scans
- Reconnaissance tab for viewing results
- Whitelist tab for managing notifications
- Reports tab for generating reports

### Check Database
```sql
-- Via phpMyAdmin or SSH
mysql -u anomradar -p

USE anomradar;
SHOW TABLES;
SELECT COUNT(*) FROM scans;
```

---

## 🎯 URLs After Deployment

| Component | URL |
|-----------|-----|
| Frontend UI | https://anomfin.fi/radar-ui |
| API Base | https://anomfin.fi/api/radar |
| List Scans | https://anomfin.fi/api/radar/scans |
| Reports | https://anomfin.fi/api/radar/reports |

---

## 📞 Support

If you encounter issues:

1. **Check logs:**
   - PHP errors: Check cPanel error logs
   - Application logs: `api/logs/` (if configured)

2. **Verify configuration:**
   - Database credentials in `api/.env`
   - FTP settings in `deployment/.env.ftp`
   - File permissions (755/644)

3. **Test components:**
   - Database connection via phpMyAdmin
   - API endpoint via curl
   - Frontend loading in browser

4. **Review documentation:**
   - [README.md](../README.md)
   - [HOWTO.md](../HOWTO.md)
   - [installer/README.md](../installer/README.md)

---

## 🎉 Success!

Once deployed, you can:
- ✅ Access the web interface at https://anomfin.fi/radar-ui
- ✅ Run security scans on companies
- ✅ Generate HTML and PDF reports
- ✅ Manage notification whitelist
- ✅ View scan history and results

The backend scanner can run locally and connect to the remote MySQL database via SSH tunnel.

**Enjoy AnomRadar on anomfin.fi! 🚀**
