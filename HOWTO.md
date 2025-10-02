# AnomRadar - Complete Setup Guide

**Get AnomRadar running in 10 minutes with this step-by-step guide!**

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] A Linux server (Ubuntu 20.04+, Debian 11+, CentOS 8+, or RHEL 8+)
- [ ] Root/sudo access to the server
- [ ] At least 2GB RAM and 10GB disk space
- [ ] Internet connection
- [ ] A domain name or IP address (optional but recommended)

---

## 🚀 Part 1: Installation (5 minutes)

### Step 1: Access Your Server

```bash
# SSH into your server
ssh username@your-server-ip

# Become root
sudo su -
```

### Step 2: Clone the Repository

```bash
# Install git if not already installed
apt-get update && apt-get install -y git   # Ubuntu/Debian
# OR
yum install -y git                         # CentOS/RHEL

# Clone AnomRadar
cd /opt
git clone https://github.com/AnomFIN/AnomRadar.git
cd AnomRadar
```

### Step 3: Run the Automated Installer

```bash
# Make installer executable
chmod +x installer/install.sh

# Run the installer
./installer/install.sh
```

**What the installer does:**
- ✅ Installs Node.js 18+, PHP 8.1+, MySQL 8.0
- ✅ Installs system tools (nmap, dig, curl)
- ✅ Creates MySQL database `anomradar`
- ✅ Creates database user `anomradar`
- ✅ Installs all dependencies
- ✅ Sets up directories with correct permissions
- ✅ Creates configuration file templates

**Expected output:**
```
✓ System dependencies installed
✓ Directories created
✓ Node.js dependencies installed
✓ PHP dependencies installed
✓ Database configured
✓ Configuration files created
================================
Installation Complete!
================================
```

**If you see errors:**
- Check `/var/log/anomradar/install.log` for details
- Ensure you're running as root
- Verify internet connection is stable

---

## ⚙️ Part 2: Configuration (3 minutes)

### Step 4: Configure Database Password

**Edit Backend Configuration:**
```bash
nano /opt/anomradar/backend/.env
```

Change this line:
```bash
DB_PASSWORD=change_this_password
```

To a secure password:
```bash
DB_PASSWORD=MySecure2024!Pass
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

**Edit API Configuration:**
```bash
nano /opt/anomradar/api/.env
```

Change the same line:
```bash
DB_PASSWORD=MySecure2024!Pass    # Must match backend!
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 5: Update Database Password in MySQL

```bash
mysql -u root -p
```

Enter your MySQL root password (set during installation), then run:

```sql
ALTER USER 'anomradar'@'localhost' IDENTIFIED BY 'MySecure2024!Pass';
FLUSH PRIVILEGES;
EXIT;
```

### Step 6: Configure Optional API Keys (OPTIONAL)

**YTJ API (Finnish Business Registry):**
1. Register at https://www.avoindata.fi/
2. Get your API key
3. Add to `/opt/anomradar/backend/.env`:
   ```bash
   YTJ_API_KEY=your_actual_api_key_here
   ```

**OWASP ZAP (Security Scanner):**
1. Install ZAP: https://www.zaproxy.org/download/
2. Start ZAP in daemon mode:
   ```bash
   zap.sh -daemon -port 8080 -config api.key=your_zap_key
   ```
3. Add to `/opt/anomradar/backend/.env`:
   ```bash
   ZAP_API_KEY=your_zap_key
   ZAP_API_URL=http://localhost:8080
   ```

**Note:** The system works without these API keys, but with limited functionality.

---

## 🌐 Part 3: Web Server Setup (5 minutes)

### Step 7: Install and Configure Nginx (Recommended)

**Install Nginx:**
```bash
apt-get install -y nginx php8.1-fpm    # Ubuntu/Debian
# OR
yum install -y nginx php-fpm           # CentOS/RHEL
```

**Create Nginx Configuration:**
```bash
nano /etc/nginx/sites-available/anomradar
```

**Paste this configuration** (replace `your-domain.com` with your actual domain or server IP):

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change this!

    root /opt/anomradar;

    # Frontend - Static Files
    location / {
        root /opt/anomradar/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API - PHP Backend
    location /api {
        alias /opt/anomradar/api/public;
        index index.php;
        
        try_files $uri $uri/ @api;
        
        location ~ \.php$ {
            fastcgi_split_path_info ^(.+\.php)(/.+)$;
            fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
            fastcgi_index index.php;
            include fastcgi_params;
            fastcgi_param SCRIPT_FILENAME $request_filename;
            fastcgi_param PATH_INFO $fastcgi_path_info;
        }
    }
    
    location @api {
        rewrite /api/(.*)$ /api/index.php?/$1 last;
    }
}
```

**Enable the site:**
```bash
ln -s /etc/nginx/sites-available/anomradar /etc/nginx/sites-enabled/
```

**Test and reload Nginx:**
```bash
nginx -t
systemctl reload nginx
systemctl enable nginx
systemctl start nginx
```

**Verify Nginx is running:**
```bash
systemctl status nginx
```

You should see: `Active: active (running)`

---

## 🔧 Part 4: Start Backend Service (2 minutes)

### Step 8: Build TypeScript Backend

```bash
cd /opt/anomradar/backend
npm run build
```

**Expected output:**
```
> anomradar-backend@1.0.0 build
> tsc
```

### Step 9: Start Backend (Two Options)

**Option A: Foreground (for testing):**
```bash
cd /opt/anomradar/backend
npm start
```

You should see:
```
✓ AnomRadar Backend Scanner is ready
  Simulation Mode: OFF
  Max Concurrent Scans: 3
  Notifications: DISABLED
```

**Keep this terminal open!** Open a new terminal to continue.

**Option B: Background Service (recommended for production):**

Create systemd service:
```bash
nano /etc/systemd/system/anomradar-backend.service
```

Paste this:
```ini
[Unit]
Description=AnomRadar Backend Scanner
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/anomradar/backend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/node /opt/anomradar/backend/dist/index.js
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/anomradar/backend.log
StandardError=append:/var/log/anomradar/backend-error.log

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
systemctl daemon-reload
systemctl enable anomradar-backend
systemctl start anomradar-backend
systemctl status anomradar-backend
```

---

## ✅ Part 5: Verification (2 minutes)

### Step 10: Test All Components

**Test 1: Check Backend Health**
```bash
curl http://localhost/api/health
```

Expected: `{"success":true,"data":{"status":"ok","timestamp":...}}`

**Test 2: Check Database Connection**
```bash
mysql -u anomradar -p'MySecure2024!Pass' -e "SHOW TABLES;" anomradar
```

Expected: List of 7 tables (scans, domains, findings, reports, whitelist, notifications, audit_log)

**Test 3: Access Web Interface**

Open your browser and go to:
```
http://your-domain.com
```
or
```
http://your-server-ip
```

You should see the AnomRadar interface with 4 tabs:
- **Search** - Start scans
- **Reconnaissance** - View scans
- **Whitelist** - Manage notifications
- **Reports** - Generate reports

---

## 🎯 Part 6: Your First Scan (1 minute)

### Step 11: Run a Test Scan

1. Open the web interface
2. Click the **Search** tab
3. Enter a company name (e.g., "Example Company" or "Google")
4. Click **Start Scan**
5. Click the **Reconnaissance** tab to see scan progress
6. Wait for scan to complete (usually 1-3 minutes)
7. Click on the scan to see results

**What gets scanned:**
- ✅ Company information (if YTJ API configured)
- ✅ Domain discovery
- ✅ DNS records and security
- ✅ Email security (SPF/DMARC/DKIM)
- ✅ SSL/TLS certificates
- ✅ Open ports and services
- ✅ Website technologies
- ✅ Security headers
- ✅ Contact information
- ✅ Social media presence
- ✅ WHOIS data

### Step 12: Generate Your First Report

1. Go to the **Reports** tab
2. Enter the Scan ID from your completed scan
3. Click **Load Reports**
4. Click **Generate PDF Report**
5. Click **Download** to save the report

---

## 🔒 Part 7: Security Hardening (OPTIONAL)

### Enable HTTPS with Let's Encrypt

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d your-domain.com

# Auto-renewal
systemctl enable certbot.timer
```

### Set Up Firewall

```bash
# Allow HTTP, HTTPS, and SSH only
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Enable Data Purge Cron Job

```bash
crontab -e
```

Add this line:
```
0 2 * * * curl -X POST http://localhost/api/maintenance/purge >/dev/null 2>&1
```

This runs daily at 2:00 AM to delete data older than 90 days.

---

## 🛠️ Troubleshooting

### Issue: "Database connection failed"

**Solution:**
```bash
# Check MySQL is running
systemctl status mysql

# Verify password is correct
mysql -u anomradar -p

# Check .env files have matching passwords
grep DB_PASSWORD /opt/anomradar/backend/.env
grep DB_PASSWORD /opt/anomradar/api/.env
```

### Issue: "Backend not starting"

**Solution:**
```bash
# Check logs
tail -50 /var/log/anomradar/backend.log
tail -50 /var/log/anomradar/backend-error.log

# Rebuild backend
cd /opt/anomradar/backend
npm install
npm run build
npm start
```

### Issue: "API returns 404"

**Solution:**
```bash
# Check Nginx config
nginx -t

# Check PHP-FPM is running
systemctl status php8.1-fpm

# Check Nginx error log
tail -50 /var/log/nginx/error.log

# Verify API directory permissions
ls -la /opt/anomradar/api/public/
```

### Issue: "Scans stuck in pending"

**Solution:**
```bash
# Check backend service
systemctl status anomradar-backend

# Restart if needed
systemctl restart anomradar-backend

# Check if backend can connect to database
cd /opt/anomradar/backend
node -e "require('mysql2').createConnection({host:'localhost',user:'anomradar',password:'MySecure2024!Pass',database:'anomradar'}).connect(err=>console.log(err||'OK'))"
```

### Issue: "Reports not generating"

**Solution:**
```bash
# Check report directory exists and is writable
mkdir -p /var/www/anomradar/api/reports/generated
chown -R www-data:www-data /var/www/anomradar

# Check TCPDF is installed
cd /opt/anomradar/api
composer show tecnickcom/tcpdf
```

---

## 📊 What You Should Have Now

After completing this guide, you should have:

- ✅ AnomRadar fully installed and running
- ✅ Web interface accessible via browser
- ✅ Backend scanner processing scans
- ✅ Database storing results
- ✅ Ability to generate PDF/HTML reports
- ✅ (Optional) SSL/HTTPS enabled
- ✅ (Optional) Automatic data purge configured

---

## 🎓 Next Steps

### Learn the Features

1. **Whitelist Management** - Add Telegram/WhatsApp contacts for notifications
2. **Custom Risk Thresholds** - Adjust scoring in backend/.env
3. **Multiple Scans** - Run concurrent scans (max 3 by default)
4. **Report Customization** - Modify report templates in api/src/Reports/

### Advanced Configuration

- **Increase Concurrent Scans**: Edit `MAX_CONCURRENT_SCANS` in backend/.env
- **Change Scan Timeout**: Edit `SCAN_TIMEOUT` in backend/.env (default: 5 minutes)
- **Modify Data Retention**: Edit `DATA_RETENTION_DAYS` in api/.env (default: 90 days)
- **Enable Notifications**: Set up Telegram bot and add to whitelist

### Integration

- **API Integration**: Use REST API for automated scanning
- **Scheduled Scans**: Set up cron jobs to scan regularly
- **Monitoring**: Integrate with Nagios, Zabbix, or Prometheus
- **Webhooks**: Receive scan completion notifications

---

## 📞 Need Help?

- **Documentation**: Check README.md, ARCHITECTURE.md, PROJECT_PLAN.md
- **Logs**: Always check logs first in `/var/log/anomradar/`
- **GitHub Issues**: https://github.com/AnomFIN/AnomRadar/issues
- **GitHub Discussions**: https://github.com/AnomFIN/AnomRadar/discussions

---

## 🎉 Congratulations!

You now have a fully functional OSINT security scanning platform!

**Quick Reference Commands:**

```bash
# Check status
systemctl status anomradar-backend
systemctl status nginx
systemctl status mysql

# View logs
tail -f /var/log/anomradar/backend.log
tail -f /var/log/nginx/access.log

# Restart services
systemctl restart anomradar-backend
systemctl restart nginx

# Run manual scan via API
curl -X POST http://localhost/api/scans \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Test Company"}'

# Manual data purge
curl -X POST http://localhost/api/maintenance/purge
```

**Happy scanning! 🔒**
