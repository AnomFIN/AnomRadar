#!/bin/bash
# AnomRadar Remote MySQL Database Setup Script
# This script helps set up the MySQL database on anomfin.fi

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "======================================"
echo "AnomRadar MySQL Setup for anomfin.fi"
echo "======================================"
echo ""

# Load FTP configuration
if [ ! -f "$SCRIPT_DIR/.env.ftp" ]; then
    echo "Error: .env.ftp file not found!"
    echo "Please copy .env.ftp.example to .env.ftp and configure it."
    exit 1
fi

source "$SCRIPT_DIR/.env.ftp"

echo "This script will help you set up the MySQL database on anomfin.fi"
echo ""
echo "Database Configuration:"
echo "  Host: $REMOTE_DB_HOST"
echo "  Database: $REMOTE_DB_NAME"
echo "  User: $REMOTE_DB_USER"
echo ""

read -p "Do you want to continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Check if migration file exists
MIGRATION_FILE="$PROJECT_ROOT/api/migrations/001_initial_schema.sql"
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "Error: Migration file not found at $MIGRATION_FILE"
    exit 1
fi

echo ""
echo "SQL commands to run on your MySQL server:"
echo "=========================================="
echo ""
cat <<EOF
-- Connect to MySQL as root or admin user
mysql -u root -p

-- Then run these commands:
CREATE DATABASE IF NOT EXISTS ${REMOTE_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${REMOTE_DB_USER}'@'localhost' IDENTIFIED BY '${REMOTE_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${REMOTE_DB_NAME}.* TO '${REMOTE_DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EXIT;

-- Then import the schema:
mysql -u ${REMOTE_DB_USER} -p ${REMOTE_DB_NAME} < api/migrations/001_initial_schema.sql
EOF

echo ""
echo "=========================================="
echo ""
echo "Option 1: Manual Setup via SSH/cPanel"
echo "  1. Copy the SQL commands above"
echo "  2. Execute them on your MySQL server"
echo "  3. Import the schema file from api/migrations/001_initial_schema.sql"
echo ""
echo "Option 2: Upload and execute via FTP + SSH"
echo "  Run: ./deployment/deploy-database.sh"
echo ""
echo "Schema file location: $MIGRATION_FILE"
echo ""

# Optionally upload schema file via FTP
read -p "Upload schema file to server via FTP? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ "$FTP_USE_SSL" = "true" ]; then
        FTP_PROTOCOL="ftps://"
    else
        FTP_PROTOCOL="ftp://"
    fi
    
    echo "Uploading schema file..."
    lftp -c "
    set ftp:ssl-allow ${FTP_USE_SSL};
    set ssl:verify-certificate no;
    open ${FTP_PROTOCOL}${FTP_USER}:${FTP_PASSWORD}@${FTP_HOST}:${FTP_PORT};
    mkdir -p ${FTP_REMOTE_API_PATH}/migrations;
    put $MIGRATION_FILE -o ${FTP_REMOTE_API_PATH}/migrations/001_initial_schema.sql;
    bye
    "
    
    echo "✓ Schema file uploaded to ${FTP_REMOTE_API_PATH}/migrations/"
    echo ""
    echo "You can now run the migration via SSH:"
    echo "  mysql -u ${REMOTE_DB_USER} -p ${REMOTE_DB_NAME} < ${FTP_REMOTE_API_PATH}/migrations/001_initial_schema.sql"
fi

echo ""
echo "Setup instructions complete!"
