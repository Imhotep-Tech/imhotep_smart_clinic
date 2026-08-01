from django.core.management.base import BaseCommand
from django.core.management import call_command
import sys
import os

class Command(BaseCommand):
    help = 'Single-command production deployment: runs migrations, clinic data linking, and collectstatic.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Starting single-command production deployment..."))

        # 1. Run migrations
        self.stdout.write(self.style.SUCCESS("⚙️ [1/4] Running database migrations..."))
        call_command('migrate', interactive=False)

        # 2. Import backup data if present
        self.stdout.write(self.style.SUCCESS("📥 [2/4] Importing backup data..."))
        call_command('import_backup_data')

        # 3. Run clinic data migration
        self.stdout.write(self.style.SUCCESS("🏥 [3/4] Linking patients and doctor profiles to clinic..."))
        call_command('migrate_clinic_data')

        # 4. Collect static files
        self.stdout.write(self.style.SUCCESS("📦 [4/4] Collecting static files..."))
        call_command('collectstatic', interactive=False)

        # 4. Touch WSGI file to reload server
        self.stdout.write(self.style.SUCCESS("🔄 Triggering WSGI server reload..."))
        try:
            os.system("touch /var/www/*_wsgi.py 2>/dev/null || true")
            os.system("touch imhotep_smart_clinic/wsgi.py 2>/dev/null || true")
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS("🎉 SUCCESS: Production deployment completed!"))
