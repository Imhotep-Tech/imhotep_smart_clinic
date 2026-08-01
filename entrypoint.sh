#!/bin/sh

if [ "$database_type" = "postgresql" ]
then
    echo "Waiting for database..."

    DB_HOST="${DATABASE_HOST:-db}"
    DB_PORT="${DATABASE_PORT:-5432}"
    DB_USER="${POSTGRES_USER:-imhotepclinic_user}"

    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
      sleep 0.5
    done

    echo "PostgreSQL started"
fi

# Reset migrations if there are conflicts
echo "Checking for migration conflicts..."
if python manage.py migrate --check 2>&1 | grep -q "InconsistentMigrationHistory"; then
    echo "Migration conflicts detected. Resetting database..."
    
    # Reset database
    python manage.py shell -c "
from django.db import connection;
cursor = connection.cursor();
cursor.execute('DROP SCHEMA public CASCADE;');
cursor.execute('CREATE SCHEMA public;');
cursor.execute('GRANT ALL ON SCHEMA public TO postgres;');
cursor.execute('GRANT ALL ON SCHEMA public TO public;');
print('Database schema reset')
"
    
    echo "Database reset complete. Creating fresh migrations..."
fi

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations doctor
python manage.py makemigrations assistant
python manage.py makemigrations
python manage.py migrate

# Import backup data if present
echo "Importing backup data if database_2026-07-30.db is present..."
python manage.py import_backup_data

# Migrate legacy data to clinic structure
echo "Migrating legacy data to clinic structure..."
python manage.py migrate_clinic_data

# Create or reset admin superuser
echo "Configuring superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True, 'email_verify': True, 'user_type': 'doctor'});
admin_user.set_password('admin123');
admin_user.email_verify = True;
admin_user.is_active = True;
admin_user.is_superuser = True;
admin_user.is_staff = True;
admin_user.save();
print('Superuser configured: username=admin, password=admin123')
"

# Start the application
exec "$@"

echo "Starting Gunicorn Web Server..."
# Start the server (Make sure the wsgi name matches your project exactly)
exec gunicorn --bind 0.0.0.0:8000 imhotep_smart_clinic.wsgi:application