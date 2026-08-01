#!/bin/bash
# ==============================================================================
# Imhotep Smart Clinic - Single-Command Production Deployment Script
# Target: Production / MySQL / PythonAnywhere (No Docker)
# ==============================================================================

set -e

echo "=================================================="
echo "🚀 Imhotep Smart Clinic - Production Deployment"
echo "=================================================="

# 1. Pull latest changes if in git workspace
if [ -d ".git" ]; then
    echo "📥 [1/4] Pulling latest updates from Git repository..."
    git pull || echo "⚠️ Git pull notice: proceed with local files"
fi

# 2. Apply all Django database migrations on MySQL
echo "⚙️ [2/5] Applying database migrations..."
python manage.py migrate --noinput

# 3. Import backup database file if available
echo "📥 [3/5] Importing backup data from database_2026-07-30.db..."
python manage.py import_backup_data

# 4. Run clinic data linking command
echo "🏥 [4/5] Linking patients, doctors, and clinic data..."
python manage.py migrate_clinic_data

# 5. Collect static assets for production web server
echo "📦 [5/5] Collecting static files..."
python manage.py collectstatic --noinput

# 5. Automatically touch WSGI configuration to trigger server reload
echo "🔄 Reloading Web Server WSGI process..."
if ls /var/www/*_wsgi.py 1> /dev/null 2>&1; then
    touch /var/www/*_wsgi.py
    echo "✅ Touched PythonAnywhere WSGI configuration for instant app reload."
fi
touch imhotep_smart_clinic/wsgi.py 2>/dev/null || true

echo "=================================================="
echo "🎉 SUCCESS: Production deployment complete!"
echo "=================================================="
