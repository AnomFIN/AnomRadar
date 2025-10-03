# AnomRadar Quick Start Guide

Get AnomRadar up and running in 5 minutes!

## Prerequisites

- Linux system (Ubuntu 20.04+ or Debian 11+ recommended)
- Root/sudo access
- Internet connection

## Step 1: Clone the Repository

```bash
git clone https://github.com/AnomFIN/AnomRadar.git
cd AnomRadar
```

## Step 2: Run the Installer

```bash
sudo chmod +x installer/install.sh
sudo installer/install.sh
```

The installer will:
- ✅ Install Node.js, PHP, MySQL, nmap, dig
- ✅ Create database and user
- ✅ Install dependencies
- ✅ Set up directories
- ✅ Create configuration files

**Expected duration:** 3-5 minutes

## Step 3: Configure

### Backend Configuration

Edit `/opt/anomradar/backend/.env`:

```bash
sudo nano /opt/anomradar/backend/.env
```

**Required changes:**
```bash
DB_PASSWORD=your_secure_password  # Change this!

# Optional: Add API keys if you have them
YTJ_API_KEY=your_ytj_api_key      # Finnish business registry
ZAP_API_KEY=your_zap_api_key      # OWASP ZAP (if installed)
```

### API Configuration

Edit `/opt/anomradar/api/.env`:

```bash
sudo nano /opt/anomradar/api/.env
```

**Required changes:**
```bash
DB_PASSWORD=your_secure_password  # Must match backend!
```

## Step 4: Start the Backend

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

Keep this terminal open, or set up as a service (see Step 6).

## Step 5: Configure Web Server

### Option A: Nginx

Create `/etc/nginx/sites-available/anomradar`:

```nginx
server {
    listen 80;
    server_name anomradar.local;  # Change to your domain

    # Frontend
    location / {
        root /opt/anomradar/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api {
        root /opt/anomradar/api/public;
        try_files $uri /index.php?$args;
        
        location ~ \.php$ {
            include fastcgi_params;
            fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        }
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/anomradar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option B: Apache

Create `/etc/apache2/sites-available/anomradar.conf`:

```apache
<VirtualHost *:80>
    ServerName anomradar.local
    DocumentRoot /opt/anomradar/frontend

    <Directory /opt/anomradar/frontend>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    Alias /api /opt/anomradar/api/public
    <Directory /opt/anomradar/api/public>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
        DirectoryIndex index.php

        <FilesMatch \.php$>
            SetHandler "proxy:unix:/var/run/php/php8.1-fpm.sock|fcgi://localhost"
        </FilesMatch>
    </Directory>
</VirtualHost>
```

Enable site:
```bash
sudo a2ensite anomradar
sudo a2enmod proxy proxy_fcgi rewrite
sudo systemctl reload apache2
```

## Step 6: Set Up as System Service (Optional)

Create `/etc/systemd/system/anomradar-backend.service`:

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

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable anomradar-backend
sudo systemctl start anomradar-backend
sudo systemctl status anomradar-backend
```

## Step 7: Access the Web Interface

Open your browser:
```
http://anomradar.local/
```

Or use IP address:
```
http://YOUR_SERVER_IP/
```

## Step 8: Run Your First Scan

1. Click on **Search** tab
2. Enter a company name (e.g., "Example Company")
3. Click **Start Scan**
4. Switch to **Reconnaissance** tab to see scan progress
5. View results when completed

## Step 9: Generate a Report

1. Go to **Reports** tab
2. Enter the Scan ID from your completed scan
3. Click **Load Reports**
4. Click **Generate PDF Report** or **Generate HTML Report**
5. Download the report

## Step 10: Set Up Data Purge (Optional)

Add cron job to purge data older than 90 days:

```bash
sudo crontab -e
```

Add this line:
```
0 2 * * * curl -X POST http://localhost/api/maintenance/purge
```

This runs daily at 2:00 AM.

---

## Common Issues & Solutions

### Issue: "Database connection failed"

**Solution:**
```bash
# Check MySQL is running
sudo systemctl status mysql

# Verify credentials
mysql -u anomradar -p
# Use password from .env file

# Reset password if needed
mysql -u root -p
mysql> ALTER USER 'anomradar'@'localhost' IDENTIFIED BY 'your_password';
mysql> FLUSH PRIVILEGES;
```

### Issue: "Cannot find module"

**Solution:**
```bash
cd /opt/anomradar/backend
sudo npm install
sudo npm run build
```

### Issue: "API returns 404"

**Solution:**
- Check web server config
- Verify PHP-FPM is running: `sudo systemctl status php8.1-fpm`
- Check error logs: `sudo tail -f /var/log/nginx/error.log`

### Issue: "Scan stuck in pending"

**Solution:**
- Backend service not running
- Start it: `cd /opt/anomradar/backend && npm start`
- Or: `sudo systemctl start anomradar-backend`

---

## Verify Installation

Run these checks:

```bash
# 1. Check backend
curl http://localhost:3000/health  # Should return OK if custom health endpoint

# 2. Check API
curl http://localhost/api/health  # Should return {"success":true,"data":{"status":"ok"}}

# 3. Check database
mysql -u anomradar -p -e "SHOW DATABASES;"  # Should list 'anomradar'

# 4. Check scans table
mysql -u anomradar -p anomradar -e "SHOW TABLES;"  # Should list all tables

# 5. Check logs
tail -f /var/log/anomradar/backend.log
tail -f /var/log/anomradar/api.log
```

---

## Default Settings

- **Simulation Mode:** OFF (real scans)
- **Max Concurrent Scans:** 3
- **Scan Timeout:** 300 seconds (5 minutes)
- **Data Retention:** 90 days
- **Notifications:** DISABLED by default

---

## Next Steps

1. **Configure API Keys** (optional):
   - YTJ API key for Finnish company lookups
   - OWASP ZAP for security scanning
   
2. **Set Up Notifications** (optional):
   - Add Telegram bot token
   - Add WhatsApp API key
   - Add contacts to whitelist

3. **Customize Risk Scoring:**
   - Edit thresholds in `.env`
   - Default: High=70, Medium=40, Low=20

4. **Add to Monitoring:**
   - Set up Nagios/Zabbix checks
   - Monitor disk space for reports
   - Monitor MySQL performance

---

## Documentation

- **Full Documentation:** [README.md](README.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Implementation Details:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Project Plan:** [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Installer Guide:** [installer/README.md](installer/README.md)

---

## Support

- **Issues:** https://github.com/AnomFIN/AnomRadar/issues
- **Discussions:** https://github.com/AnomFIN/AnomRadar/discussions

---

## Security Reminder

⚠️ **AnomRadar performs PASSIVE scanning only**
- No active attacks or exploits
- Read-only operations
- Respects robots.txt
- Always obtain authorization before scanning

---

**You're ready to go! Happy scanning! 🔒**
