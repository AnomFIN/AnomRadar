#!/bin/bash
# AnomRadar FTP Deployment Script for anomfin.fi
# This script deploys the PHP API and frontend to anomfin.fi via FTP

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "======================================"
echo "AnomRadar FTP Deployment to anomfin.fi"
echo "======================================"
echo ""

# Load FTP configuration
if [ ! -f "$SCRIPT_DIR/.env.ftp" ]; then
    echo "Error: .env.ftp file not found!"
    echo "Please copy .env.ftp.example to .env.ftp and configure it."
    exit 1
fi

source "$SCRIPT_DIR/.env.ftp"

# Validate required variables
if [ -z "$FTP_HOST" ] || [ -z "$FTP_USER" ] || [ -z "$FTP_PASSWORD" ]; then
    echo "Error: FTP credentials not configured in .env.ftp"
    exit 1
fi

# Create temporary deployment directory
TEMP_DIR="/tmp/anomradar-deploy-$(date +%s)"
mkdir -p "$TEMP_DIR"

echo "Preparing deployment files..."

# Function to deploy via FTP
deploy_ftp() {
    local local_path=$1
    local remote_path=$2
    local description=$3
    
    echo ""
    echo "Deploying $description..."
    echo "  Local:  $local_path"
    echo "  Remote: $remote_path"
    
    if [ "$FTP_USE_SSL" = "true" ]; then
        FTP_PROTOCOL="ftps://"
    else
        FTP_PROTOCOL="ftp://"
    fi
    
    lftp -c "
    set ftp:ssl-allow ${FTP_USE_SSL};
    set ssl:verify-certificate no;
    open ${FTP_PROTOCOL}${FTP_USER}:${FTP_PASSWORD}@${FTP_HOST}:${FTP_PORT};
    mirror --reverse --delete --verbose --exclude .git/ --exclude .env --exclude node_modules/ --exclude vendor/ $local_path $remote_path;
    bye
    "
    
    if [ $? -eq 0 ]; then
        echo "✓ $description deployed successfully"
    else
        echo "✗ Failed to deploy $description"
        return 1
    fi
}

# Backup existing deployment (if enabled)
if [ "$BACKUP_ENABLED" = "true" ]; then
    echo ""
    echo "Creating backup..."
    mkdir -p "$BACKUP_PATH"
    BACKUP_FILE="$BACKUP_PATH/anomradar-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    # Download current deployment for backup
    if [ "$FTP_USE_SSL" = "true" ]; then
        FTP_PROTOCOL="ftps://"
    else
        FTP_PROTOCOL="ftp://"
    fi
    
    lftp -c "
    set ftp:ssl-allow ${FTP_USE_SSL};
    set ssl:verify-certificate no;
    open ${FTP_PROTOCOL}${FTP_USER}:${FTP_PASSWORD}@${FTP_HOST}:${FTP_PORT};
    mirror --verbose $FTP_REMOTE_API_PATH $TEMP_DIR/api-backup;
    mirror --verbose $FTP_REMOTE_FRONTEND_PATH $TEMP_DIR/frontend-backup;
    bye
    " 2>/dev/null || echo "Note: Backup skipped (may be first deployment)"
    
    if [ -d "$TEMP_DIR/api-backup" ] || [ -d "$TEMP_DIR/frontend-backup" ]; then
        tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" . 2>/dev/null || true
        echo "✓ Backup saved to $BACKUP_FILE"
    fi
fi

# Deploy PHP API
echo ""
echo "Step 1: Deploying PHP API to $FTP_REMOTE_API_PATH..."
if [ -d "$PROJECT_ROOT/api" ]; then
    # Create .env file for remote server
    cat > "$PROJECT_ROOT/api/.env.remote" <<EOF
# API Configuration for anomfin.fi
DB_HOST=${REMOTE_DB_HOST}
DB_PORT=${REMOTE_DB_PORT}
DB_NAME=${REMOTE_DB_NAME}
DB_USER=${REMOTE_DB_USER}
DB_PASSWORD=${REMOTE_DB_PASSWORD}
DB_CHARSET=${REMOTE_DB_CHARSET}

DATA_RETENTION_DAYS=90

REPORT_OUTPUT_PATH=${FTP_REMOTE_REPORTS_PATH}/generated
REPORT_BASE_URL=${REMOTE_REPORT_BASE_URL}

API_KEY=your_secure_api_key_here
CORS_ALLOWED_ORIGINS=https://anomfin.fi,https://www.anomfin.fi

LOG_LEVEL=info
LOG_FILE=/tmp/anomradar-api.log

APP_ENV=production
APP_DEBUG=false
EOF
    
    echo "✓ Created remote .env configuration"
    echo ""
    echo "IMPORTANT: After deployment, manually:"
    echo "  1. Rename api/.env.remote to api/.env on the server"
    echo "  2. Update database credentials in the .env file"
    echo "  3. Run database migrations if needed"
    echo ""
    
    deploy_ftp "$PROJECT_ROOT/api" "$FTP_REMOTE_API_PATH" "PHP API"
else
    echo "Error: API directory not found at $PROJECT_ROOT/api"
    exit 1
fi

# Deploy Frontend
echo ""
echo "Step 2: Deploying Frontend to $FTP_REMOTE_FRONTEND_PATH..."
if [ -d "$PROJECT_ROOT/frontend" ]; then
    # Update API base URL in frontend for production
    mkdir -p "$TEMP_DIR/frontend"
    cp -r "$PROJECT_ROOT/frontend"/* "$TEMP_DIR/frontend/"
    
    # Update app.js with production API URL
    sed -i "s|const API_BASE_URL = window.location.hostname === 'localhost'|const API_BASE_URL = window.location.hostname.includes('localhost')|g" "$TEMP_DIR/frontend/js/app.js" 2>/dev/null || true
    sed -i "s|: '/api'|: '${REMOTE_API_BASE_URL}'|g" "$TEMP_DIR/frontend/js/app.js" 2>/dev/null || true
    
    deploy_ftp "$TEMP_DIR/frontend" "$FTP_REMOTE_FRONTEND_PATH" "Frontend (Browser GUI)"
else
    echo "Error: Frontend directory not found at $PROJECT_ROOT/frontend"
    exit 1
fi

# Create reports directory on remote server
echo ""
echo "Step 3: Creating reports directory..."
if [ "$FTP_USE_SSL" = "true" ]; then
    FTP_PROTOCOL="ftps://"
else
    FTP_PROTOCOL="ftp://"
fi

lftp -c "
set ftp:ssl-allow ${FTP_USE_SSL};
set ssl:verify-certificate no;
open ${FTP_PROTOCOL}${FTP_USER}:${FTP_PASSWORD}@${FTP_HOST}:${FTP_PORT};
mkdir -p ${FTP_REMOTE_REPORTS_PATH}/generated;
bye
" 2>/dev/null || true

echo "✓ Reports directory configured"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Deployed to:"
echo "  - API: https://anomfin.fi/api/radar"
echo "  - Frontend: https://anomfin.fi/radar-ui"
echo ""
echo "Post-deployment steps:"
echo "  1. Access your FTP server and rename api/.env.remote to api/.env"
echo "  2. Update database credentials in api/.env"
echo "  3. Ensure MySQL database is created and configured"
echo "  4. Run database migrations: mysql -u $REMOTE_DB_USER -p $REMOTE_DB_NAME < api/migrations/001_initial_schema.sql"
echo "  5. Set proper file permissions (chmod 755 for directories, 644 for files)"
echo "  6. Test the frontend at https://anomfin.fi/radar-ui"
echo "  7. Test the API at https://anomfin.fi/api/radar/scans"
echo ""
echo "Backend scanner should connect to:"
echo "  - API URL: ${REMOTE_API_BASE_URL}"
echo "  - Update backend/.env with REMOTE_DB_* credentials"
echo ""
