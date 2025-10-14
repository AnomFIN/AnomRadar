# Usage Examples - AnomRadar Deployment

## Scenario 1: Fresh Installation on Kali Linux

### Step 1: Install AnomRadar
```bash
# Clone repository
git clone https://github.com/AnomFIN/AnomRadar.git
cd AnomRadar

# Run installer (automatically detects Kali Linux)
sudo chmod +x installer/install.sh
sudo ./installer/install.sh
```

**Expected Output:**
```
================================
AnomRadar Installation Script
================================

Detected OS: kali

Installing system dependencies...
✓ System dependencies installed

Installing Node.js dependencies...
✓ Node.js dependencies installed

Installing PHP dependencies...
✓ PHP dependencies installed

✓ Database configured

Installation Complete!
```

### Step 2: Configure Environment
```bash
# Configure backend
cd /opt/anomradar/backend
sudo nano .env
# Set DB_PASSWORD and API keys

# Configure API
cd /opt/anomradar/api
sudo nano .env
# Set DB_PASSWORD
```

### Step 3: Start Backend Scanner
```bash
cd /opt/anomradar/backend
npm start
```

---

## Scenario 2: Deploy to anomfin.fi with FTP

### Prerequisites
- FTP/FTPS access to anomfin.fi
- MySQL database created on hosting server
- anomfin.fi supports PHP 8.1+ and MySQL 8.0+

### Step 1: Configure FTP Credentials
```bash
cd deployment
cp .env.ftp.example .env.ftp
nano .env.ftp
```

**Example .env.ftp configuration:**
```bash
FTP_HOST=ftp.anomfin.fi
FTP_PORT=21
FTP_USER=myusername
FTP_PASSWORD=mySecurePassword123!
FTP_USE_SSL=true

FTP_REMOTE_API_PATH=/public_html/api/radar
FTP_REMOTE_FRONTEND_PATH=/public_html/radar-ui

REMOTE_DB_HOST=localhost
REMOTE_DB_NAME=anomradar
REMOTE_DB_USER=anomradar
REMOTE_DB_PASSWORD=myDBPassword456!
```

### Step 2: Set Up MySQL Database

**Option A: Via cPanel**
1. Login to cPanel at https://anomfin.fi/cpanel
2. Go to "MySQL Databases"
3. Create database: `myuser_anomradar`
4. Create user: `myuser_anomradar`
5. Add user to database with all privileges
6. Go to phpMyAdmin
7. Select `myuser_anomradar` database
8. Click "Import"
9. Choose file: `api/migrations/001_initial_schema.sql`
10. Click "Go"

**Option B: Via SSH (if available)**
```bash
ssh user@anomfin.fi

# Create database
mysql -u root -p
CREATE DATABASE anomradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'anomradar'@'localhost' IDENTIFIED BY 'myDBPassword456!';
GRANT ALL PRIVILEGES ON anomradar.* TO 'anomradar'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Import schema
mysql -u anomradar -p anomradar < ~/public_html/api/radar/migrations/001_initial_schema.sql
```

### Step 3: Deploy to anomfin.fi
```bash
./deployment/deploy-ftp.sh
```

**Expected Output:**
```
======================================
AnomRadar FTP Deployment to anomfin.fi
======================================

Preparing deployment files...

Creating backup...
✓ Backup saved to ./backups/anomradar-backup-20241014-123456.tar.gz

Step 1: Deploying PHP API to /public_html/api/radar...
Deploying PHP API...
  Local:  /home/runner/work/AnomRadar/AnomRadar/api
  Remote: /public_html/api/radar
✓ PHP API deployed successfully

Step 2: Deploying Frontend to /public_html/radar-ui...
Deploying Frontend (Browser GUI)...
  Local:  /tmp/anomradar-deploy-1234567890/frontend
  Remote: /public_html/radar-ui
✓ Frontend (Browser GUI) deployed successfully

Step 3: Creating reports directory...
✓ Reports directory configured

======================================
Deployment Complete!
======================================

Deployed to:
  - API: https://anomfin.fi/api/radar
  - Frontend: https://anomfin.fi/radar-ui
```

### Step 4: Post-Deployment Configuration

**Via FTP Client (FileZilla, WinSCP, etc.):**
1. Connect to ftp.anomfin.fi
2. Navigate to `/public_html/api/radar/`
3. Find file: `.env.remote`
4. Rename to: `.env`
5. Edit `.env` if needed (verify database credentials)

**Via cPanel File Manager:**
1. Login to cPanel
2. Go to "File Manager"
3. Navigate to `public_html/api/radar/`
4. Right-click `.env.remote` → Rename → `.env`
5. Right-click `.env` → Edit (optional, to verify settings)

### Step 5: Verify Deployment

**Test Frontend:**
```bash
# Open in browser
https://anomfin.fi/radar-ui
```

**Test API:**
```bash
# Test API endpoint
curl https://anomfin.fi/api/radar/scans

# Expected response:
# {"status":"success","data":[],"message":"Scans retrieved successfully"}
```

**Check Database Connection:**
- Login to phpMyAdmin
- Select `anomradar` database
- Should see tables: scans, domains, findings, reports, whitelist, etc.

---

## Scenario 3: Connect Backend Scanner to Remote MySQL

### Option A: SSH Tunnel (Recommended)

**On Local Machine:**
```bash
# Create SSH tunnel to MySQL
ssh -L 3306:localhost:3306 myuser@anomfin.fi -N &

# Verify tunnel
netstat -an | grep 3306
```

**Configure backend/.env:**
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=myDBPassword456!
```

**Start Backend Scanner:**
```bash
cd /opt/anomradar/backend
npm start
```

**Test Connection:**
```bash
# The backend should connect successfully
# Check logs for "Connected to database" message
tail -f /var/log/anomradar/backend.log
```

### Option B: Direct Remote Connection (if allowed)

**Note:** Most shared hosting providers block remote MySQL connections for security.

**Configure backend/.env:**
```bash
DB_HOST=anomfin.fi
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=myDBPassword456!
```

**Test Connection:**
```bash
# Test from command line
mysql -h anomfin.fi -u anomradar -p anomradar

# If connection fails, use SSH tunnel instead
```

---

## Scenario 4: Update Existing Deployment

### Step 1: Pull Latest Changes
```bash
cd /path/to/AnomRadar
git pull origin main
```

### Step 2: Redeploy
```bash
cd deployment
./deploy-ftp.sh
```

The script automatically:
- Creates a backup of current deployment
- Uploads new files
- Preserves existing `.env` configuration

### Step 3: Verify Update
```bash
# Clear browser cache
# Reload: https://anomfin.fi/radar-ui

# Test API
curl https://anomfin.fi/api/radar/scans
```

---

## Scenario 5: Run a Security Scan

### Step 1: Access Frontend
Open browser to: https://anomfin.fi/radar-ui

### Step 2: Initiate Scan
1. Click "Search" tab
2. Enter company name: e.g., "Example Oy"
3. Click "Start Scan"

### Step 3: Monitor Progress
1. Click "Reconnaissance" tab
2. View scan progress in real-time
3. See discovered domains, findings, risk scores

### Step 4: Generate Report
1. Click "Reports" tab
2. Select completed scan
3. Click "Generate HTML Report" or "Generate PDF Report"
4. Download and review report

### Step 5: Review via API
```bash
# List all scans
curl https://anomfin.fi/api/radar/scans

# Get specific scan
curl https://anomfin.fi/api/radar/scans/1

# List reports
curl https://anomfin.fi/api/radar/reports/1
```

---

## Scenario 6: Backup and Restore

### Backup Database
```bash
# Via SSH
ssh user@anomfin.fi
mysqldump -u anomradar -p anomradar > anomradar-backup-$(date +%Y%m%d).sql

# Via phpMyAdmin
# 1. Select database
# 2. Click "Export"
# 3. Choose "Custom" method
# 4. Select "Save output to file"
# 5. Click "Go"
```

### Backup Files
```bash
# Deployment script automatically creates backups in ./backups/
ls -la deployment/backups/

# Manual backup via FTP
# Download entire /public_html/api/radar/ directory
# Download entire /public_html/radar-ui/ directory
```

### Restore Database
```bash
# Via SSH
mysql -u anomradar -p anomradar < anomradar-backup-20241014.sql

# Via phpMyAdmin
# 1. Select database
# 2. Click "Import"
# 3. Choose backup file
# 4. Click "Go"
```

### Restore Files
```bash
# Extract backup
tar -xzf deployment/backups/anomradar-backup-20241014-123456.tar.gz

# Upload via FTP or use deployment script
./deployment/deploy-ftp.sh
```

---

## Scenario 7: Troubleshooting Common Issues

### Issue: FTP Connection Fails

**Diagnosis:**
```bash
# Test FTP connection
lftp -c "open ftp://user:pass@ftp.anomfin.fi; ls; bye"
```

**Solutions:**
1. Verify FTP credentials in `.env.ftp`
2. Check if FTP service is running on anomfin.fi
3. Try FTPS: `FTP_USE_SSL=true`
4. Check firewall rules
5. Contact hosting provider

### Issue: API Returns 500 Error

**Diagnosis:**
```bash
# Check PHP error logs
ssh user@anomfin.fi
tail -f ~/logs/error.log

# Or via cPanel: Error Log viewer
```

**Solutions:**
1. Verify `.env` exists in `api/` directory (rename from `.env.remote`)
2. Check database credentials in `.env`
3. Verify PHP extensions: mysqli, pdo, json, xml, mbstring
4. Check file permissions: 644 for files, 755 for directories
5. Test database connection via phpMyAdmin

### Issue: Frontend Shows "Connection Failed"

**Diagnosis:**
```bash
# Open browser console (F12)
# Check for error messages

# Test API directly
curl https://anomfin.fi/api/radar/scans
```

**Solutions:**
1. Verify API is accessible: `curl https://anomfin.fi/api/radar/scans`
2. Check CORS settings in `api/.env`
3. Clear browser cache
4. Verify `.htaccess` exists in `api/public/`
5. Check web server configuration (Apache/Nginx)

### Issue: Backend Can't Connect to MySQL

**Diagnosis:**
```bash
# Test SSH tunnel
ssh -L 3306:localhost:3306 user@anomfin.fi -N
netstat -an | grep 3306

# Test MySQL connection
mysql -h localhost -u anomradar -p anomradar
```

**Solutions:**
1. Use SSH tunnel instead of direct connection
2. Verify database credentials
3. Check if remote MySQL is allowed (usually not on shared hosting)
4. Test connection from phpMyAdmin
5. Check MySQL user privileges

---

## Additional Resources

- **Full Deployment Guide**: [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Kali & FTP Guide**: [KALI_AND_FTP_GUIDE.md](../KALI_AND_FTP_GUIDE.md)
- **Quick Reference**: [QUICK_REFERENCE.md](../QUICK_REFERENCE.md)
- **Architecture Diagrams**: [ARCHITECTURE_DIAGRAM.md](../ARCHITECTURE_DIAGRAM.md)
- **Main Documentation**: [README.md](../README.md)

---

## Support

For issues or questions:
1. Check documentation files above
2. Review error logs
3. Test components individually
4. Open issue on GitHub: https://github.com/AnomFIN/AnomRadar/issues

**Happy scanning! 🚀🔒**
