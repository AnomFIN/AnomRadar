# AnomRadar Installer

## Overview
This directory contains installation scripts and configuration templates for AnomRadar.

## Quick Installation

### Prerequisites
- Linux-based system (**Ubuntu, Debian, Kali Linux, CentOS, RHEL, Fedora**)
- Root access (sudo)
- Internet connection

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnomFIN/AnomRadar.git
   cd AnomRadar
   ```

2. **Run the installer:**
   ```bash
   sudo chmod +x installer/install.sh
   sudo installer/install.sh
   ```

3. **Configure the system:**
   
   Edit the backend configuration:
   ```bash
   sudo nano /opt/anomradar/backend/.env
   ```
   
   Edit the API configuration:
   ```bash
   sudo nano /opt/anomradar/api/.env
   ```

4. **Important Configuration:**
   - Set `DB_PASSWORD` in both `.env` files
   - Configure YTJ API key if you have one
   - Configure ZAP API key if you're using OWASP ZAP
   - Set `SIMULATION_MODE=false` for real scans (default: false)
   - Configure notification whitelist if needed

5. **Start the backend:**
   ```bash
   cd /opt/anomradar/backend
   npm start
   ```

6. **Configure web server:**
   
   Example Nginx configuration:
   ```nginx
   server {
       listen 80;
       server_name anomradar.example.com;
       
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

## Configuration Details

### API Tokens Required

#### YTJ API (Optional)
- Register at: https://www.avoindata.fi/
- Free tier available for limited requests
- Used for Finnish company lookups

#### OWASP ZAP (Optional)
- Install ZAP: https://www.zaproxy.org/
- Start ZAP in daemon mode: `zap.sh -daemon -port 8080 -config api.key=YOUR_API_KEY`
- Used for passive security scanning

### Database Setup
The installer creates a MySQL database named `anomradar` with user `anomradar`.
Default password: `AnomRadar2025!` (CHANGE THIS IN PRODUCTION!)

### Security Notes
- **NEVER commit `.env` files with real credentials**
- Change default database passwords
- Use HTTPS in production
- Keep simulation mode OFF unless testing
- Only whitelist trusted contacts for notifications

### Data Retention
By default, scan data is automatically purged after 90 days.
Configure in `.env`: `DATA_RETENTION_DAYS=90`

Set up a cron job to run the purge:
```bash
0 2 * * * curl -X POST http://localhost/api/maintenance/purge
```

## Systemd Service (Optional)

Create `/etc/systemd/system/anomradar-backend.service`:
```ini
[Unit]
Description=AnomRadar Backend Scanner
After=network.target mysql.service

[Service]
Type=simple
User=anomradar
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

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running: `sudo systemctl status mysql`
- Check credentials in `.env` files
- Ensure database was created: `mysql -u root -p -e "SHOW DATABASES;"`

### Backend Won't Start
- Check logs: `/var/log/anomradar/backend.log`
- Verify dependencies: `cd /opt/anomradar/backend && npm install`
- Check Node.js version: `node --version` (requires 18+)

### API Returns 500 Errors
- Check PHP error logs: `/var/log/apache2/error.log` or `/var/log/nginx/error.log`
- Verify PHP extensions: `php -m | grep -E 'pdo|mysql|json|xml'`
- Check file permissions: `ls -la /opt/anomradar/api/`

### Reports Not Generating
- Check report output directory exists: `/var/www/anomradar/api/reports/generated`
- Verify write permissions: `sudo chown -R www-data:www-data /var/www/anomradar`
- Check TCPDF installation: `cd /opt/anomradar/api && composer show tecnickcom/tcpdf`

## Uninstallation

To remove AnomRadar:
```bash
sudo systemctl stop anomradar-backend
sudo systemctl disable anomradar-backend
sudo rm /etc/systemd/system/anomradar-backend.service
sudo rm -rf /opt/anomradar
sudo rm -rf /var/log/anomradar
sudo rm -rf /var/www/anomradar
mysql -u root -p -e "DROP DATABASE anomradar; DROP USER 'anomradar'@'localhost';"
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/AnomFIN/AnomRadar/issues
- Documentation: See PROJECT_PLAN.md and README.md
