#!/bin/bash
# AnomRadar Installer Script

set -e

echo "================================"
echo "AnomRadar Installation Script"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. Please install manually."
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Install dependencies based on OS
echo "Installing system dependencies..."
case "$OS" in
    ubuntu|debian|kali)
        apt-get update
        apt-get install -y nodejs npm php php-cli php-mysql php-json php-xml php-mbstring \
            mysql-server composer curl git nmap dnsutils tcpdump lftp
        ;;
    centos|rhel|fedora)
        yum install -y nodejs npm php php-cli php-mysqlnd php-json php-xml php-mbstring \
            mysql-server composer curl git nmap bind-utils tcpdump lftp
        ;;
    *)
        echo "Unsupported OS: $OS"
        echo "Please install Node.js, PHP, MySQL, nmap, and dig manually"
        exit 1
        ;;
esac

echo "✓ System dependencies installed"
echo ""

# Setup directories
echo "Setting up directories..."
INSTALL_DIR="/opt/anomradar"
mkdir -p $INSTALL_DIR
mkdir -p /var/log/anomradar
mkdir -p /var/www/anomradar/api/reports/generated

# Set permissions
chown -R www-data:www-data /var/www/anomradar 2>/dev/null || chown -R nginx:nginx /var/www/anomradar 2>/dev/null || true
chown -R www-data:www-data /var/log/anomradar 2>/dev/null || chown -R nginx:nginx /var/log/anomradar 2>/dev/null || true

echo "✓ Directories created"
echo ""

# Copy files (assuming script is run from repo root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
echo "Copying files from $SCRIPT_DIR..."
cp -r $SCRIPT_DIR/* $INSTALL_DIR/

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd $INSTALL_DIR/backend
npm ci --production
npm run build

echo "✓ Node.js dependencies installed"
echo ""

# Install PHP dependencies
echo "Installing PHP dependencies..."
cd $INSTALL_DIR/api
composer install --no-dev --optimize-autoloader

echo "✓ PHP dependencies installed"
echo ""

# Configure database
echo "Configuring database..."
echo "Please enter MySQL root password:"
mysql -u root -p <<EOF
CREATE DATABASE IF NOT EXISTS anomradar CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'anomradar'@'localhost' IDENTIFIED BY 'AnomRadar2025!';
GRANT ALL PRIVILEGES ON anomradar.* TO 'anomradar'@'localhost';
FLUSH PRIVILEGES;
EOF

# Run migrations
mysql -u anomradar -pAnomRadar2025! anomradar < $INSTALL_DIR/api/migrations/001_initial_schema.sql

echo "✓ Database configured"
echo ""

# Create configuration files
echo "Creating configuration files..."

# Backend .env
if [ ! -f $INSTALL_DIR/backend/.env ]; then
    cp $INSTALL_DIR/backend/.env.example $INSTALL_DIR/backend/.env
    echo "✓ Created backend/.env (please configure)"
fi

# API .env
if [ ! -f $INSTALL_DIR/api/.env ]; then
    cp $INSTALL_DIR/api/.env.example $INSTALL_DIR/api/.env
    echo "✓ Created api/.env (please configure)"
fi

echo ""
echo "================================"
echo "Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Configure API tokens in $INSTALL_DIR/backend/.env"
echo "2. Configure database password in $INSTALL_DIR/backend/.env and $INSTALL_DIR/api/.env"
echo "3. Set up web server (Apache/Nginx) to serve $INSTALL_DIR/frontend and $INSTALL_DIR/api/public"
echo "4. Start the backend service: cd $INSTALL_DIR/backend && npm start"
echo "5. (Optional) Set up systemd service for automatic startup"
echo ""
echo "Configuration files:"
echo "  - Backend: $INSTALL_DIR/backend/.env"
echo "  - API: $INSTALL_DIR/api/.env"
echo ""
echo "For detailed configuration, see README.md"
