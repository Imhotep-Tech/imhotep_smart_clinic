#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

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
python manage.py makemigrations doctors
python manage.py makemigrations assistant
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
" 2>/dev/null || echo "Superuser creation skipped (will retry after first successful registration)"

# Start the application
exec "$@"
