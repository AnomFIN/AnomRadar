# AnomRadar Quick Reference Card

## 🚀 Installation

### Kali Linux / Ubuntu / Debian
```bash
git clone https://github.com/AnomFIN/AnomRadar.git
cd AnomRadar
sudo ./installer/install.sh
```

## 🌐 Deployment to anomfin.fi

### Setup
```bash
cd deployment
cp .env.ftp.example .env.ftp
nano .env.ftp  # Configure FTP and MySQL credentials
```

### Deploy
```bash
./deployment/deploy-ftp.sh
```

### Post-Deploy
1. Rename `api/.env.remote` → `api/.env` on server
2. Test: https://anomfin.fi/radar-ui

## 🔗 URLs After Deployment

| Service | URL |
|---------|-----|
| Frontend | https://anomfin.fi/radar-ui |
| API | https://anomfin.fi/api/radar |
| Scans | https://anomfin.fi/api/radar/scans |

## 🗄️ MySQL Setup

### Via cPanel/phpMyAdmin
1. Create database: `anomradar`
2. Create user: `anomradar`
3. Import: `api/migrations/001_initial_schema.sql`

### Via Script
```bash
./deployment/setup-mysql.sh
```

## 🖥️ Backend Scanner Connection

### SSH Tunnel (Recommended)
```bash
ssh -L 3306:localhost:3306 user@anomfin.fi -N &
```

Update `backend/.env`:
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=anomradar
DB_USER=anomradar
DB_PASSWORD=your_password
```

## 📦 Dependencies

### Local System
- Node.js 18+
- PHP 8.1+
- MySQL 8.0+
- lftp (for deployment)

### Remote Server (anomfin.fi)
- PHP 8.1+ with mysqli, pdo, json, xml, mbstring
- MySQL 8.0+
- Apache/Nginx

## 🛠️ Commands

### Deploy Updates
```bash
git pull origin main
./deployment/deploy-ftp.sh
```

### Start Backend Scanner
```bash
cd backend
npm start
```

### Check Status
```bash
# API test
curl https://anomfin.fi/api/radar/scans

# Database test
mysql -h localhost -u anomradar -p anomradar
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `deployment/.env.ftp` | FTP credentials (don't commit!) |
| `backend/.env` | Scanner configuration |
| `api/.env` | API configuration (on server) |
| `DEPLOYMENT.md` | Full deployment guide |

## 🔐 Security Checklist

- [ ] Use FTPS (`FTP_USE_SSL=true`)
- [ ] Strong MySQL password
- [ ] Enable HTTPS on anomfin.fi
- [ ] Protect `.env` files (chmod 600)
- [ ] Use SSH tunnel for MySQL
- [ ] Regular backups

## 🐛 Troubleshooting

### FTP fails
```bash
lftp -c "open ftp://user:pass@ftp.anomfin.fi; ls; bye"
```

### API 500 error
- Check PHP error logs in cPanel
- Verify `.env` exists on server
- Test database connection

### Frontend connection failed
- Verify API URL in browser console
- Check CORS in `api/.env`

## 📚 Documentation

- `README.md` - Main documentation
- `DEPLOYMENT.md` - Deployment guide
- `KALI_AND_FTP_GUIDE.md` - New features guide
- `HOWTO.md` - Step-by-step setup

## 🎯 Support

1. Check logs (cPanel > Error Log)
2. Test components individually
3. Review documentation
4. Check GitHub issues

---

**Quick Start: `./installer/install.sh` → configure `.env` → `./deployment/deploy-ftp.sh` → Done! 🎉**
