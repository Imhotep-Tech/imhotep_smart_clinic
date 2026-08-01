import sqlite3
import os
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils.dateparse import parse_date, parse_datetime, parse_time
from accounts.models import User
from doctor.models import DoctorProfile, Patients, MedicalRecord, Appointments, Clinic
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Imports backup data from database_2026-07-30.db into current active database engine (PostgreSQL, MySQL, SQLite).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-file',
            default='database_2026-07-30.db',
            help='Path to SQLite backup file'
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        if not os.path.exists(backup_file):
            self.stdout.write(self.style.WARNING(f"Backup file {backup_file} not found. Skipping backup import."))
            return

        # Safety check: ensure doctor_doctorprofile table and clinic_id exist before importing
        from django.db import connection as django_conn
        try:
            with django_conn.cursor() as db_cursor:
                table_names = django_conn.introspection.table_names(db_cursor)
                if 'doctor_doctorprofile' not in table_names:
                    self.stdout.write(self.style.WARNING("doctor_doctorprofile table does not exist yet. Please run 'python manage.py migrate' first."))
                    return
                columns = [col[0] for col in django_conn.introspection.get_table_description(db_cursor, 'doctor_doctorprofile')]
                if 'clinic_id' not in columns:
                    self.stdout.write(self.style.WARNING("clinic_id column does not exist on doctor_doctorprofile yet. Please run 'python manage.py migrate' first."))
                    return
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Database introspection notice: {e}"))

        conn = sqlite3.connect(backup_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        with transaction.atomic():
            # 1. Import Users (accounts_user)
            cursor.execute("SELECT * FROM accounts_user")
            users_rows = cursor.fetchall()
            users_imported = 0

            for row in users_rows:
                u_id = int(row['id'])
                username = row['username']
                
                # Find user by exact ID or username
                user_obj = User.objects.filter(id=u_id).first() or User.objects.filter(username=username).first()
                if not user_obj:
                    user_obj = User.objects.create(
                        id=u_id,
                        username=username,
                        email=row['email'] or '',
                        first_name=row['first_name'] or '',
                        last_name=row['last_name'] or '',
                        password=row['password'] or '',
                        is_staff=bool(row['is_staff'] == '1' or row['is_staff'] is True),
                        is_superuser=bool(row['is_superuser'] == '1' or row['is_superuser'] is True),
                        is_active=True,
                        email_verify=True,
                        user_type=row['user_type'] or 'doctor',
                        is_demo=bool(row['is_demo'] == '1' or row['is_demo'] is True)
                    )
                    users_imported += 1
                else:
                    # Update fields if user exists
                    if user_obj.username != username:
                        user_obj.username = username
                    user_obj.email_verify = True
                    user_obj.is_active = True
                    if row['password']:
                        user_obj.password = row['password']
                    user_obj.save()

            self.stdout.write(f"Imported/Updated {users_imported} Users.")

            # 2. Import DoctorProfiles (doctor_doctorprofile)
            cursor.execute("SELECT * FROM doctor_doctorprofile")
            doc_rows = cursor.fetchall()
            doctors_imported = 0

            for row in doc_rows:
                d_id = int(row['id'])
                user_id = int(row['user_id'])
                user_obj = User.objects.filter(id=user_id).first()

                if user_obj:
                    doc_obj = DoctorProfile.objects.filter(id=d_id).first() or DoctorProfile.objects.filter(user=user_obj).first()
                    if not doc_obj:
                        doc_obj = DoctorProfile.objects.create(
                            id=d_id,
                            user=user_obj,
                            specialization=row['specialization'] or 'General',
                            clinic_photo_path=row['clinic_photo_path'] or ''
                        )
                        doctors_imported += 1
                    else:
                        if doc_obj.user != user_obj:
                            doc_obj.user = user_obj
                        if row['specialization']:
                            doc_obj.specialization = row['specialization']
                        doc_obj.save()

            self.stdout.write(f"Imported/Updated {doctors_imported} DoctorProfiles.")

            # 3. Import Patients (doctor_patients)
            cursor.execute("SELECT * FROM doctor_patients")
            pat_rows = cursor.fetchall()
            patients_imported = 0

            for row in pat_rows:
                p_id = int(row['id'])
                doc_id = int(row['doctor_id']) if row['doctor_id'] else None
                doc_obj = DoctorProfile.objects.filter(id=doc_id).first() if doc_id else None

                pat_obj = Patients.objects.filter(id=p_id).first()
                dob = parse_date(row['date_of_birth']) if row['date_of_birth'] else None

                if not pat_obj:
                    Patients.objects.create(
                        id=p_id,
                        name=row['name'] or 'Patient',
                        doctor=doc_obj,
                        phone_number=row['phone_number'] or '',
                        gender=row['gender'] or 'Male',
                        date_of_birth=dob
                    )
                    patients_imported += 1
                else:
                    if doc_obj and pat_obj.doctor != doc_obj:
                        pat_obj.doctor = doc_obj
                        pat_obj.save()

            self.stdout.write(f"Imported/Updated {patients_imported} Patients records.")

            # 4. Import Medical Records (doctor_medicalrecord)
            cursor.execute("SELECT * FROM doctor_medicalrecord")
            mr_rows = cursor.fetchall()
            mr_imported = 0

            for row in mr_rows:
                mr_id = int(row['id'])
                doc_obj = DoctorProfile.objects.filter(id=int(row['doctor_id'])).first() if row['doctor_id'] else None
                pat_obj = Patients.objects.filter(id=int(row['patient_id'])).first() if row['patient_id'] else None

                if doc_obj and pat_obj and not MedicalRecord.objects.filter(id=mr_id).exists():
                    dt = parse_datetime(row['date']) if row['date'] else None
                    MedicalRecord.objects.create(
                        id=mr_id,
                        doctor=doc_obj,
                        patient=pat_obj,
                        details=row['details'] or '',
                        remarks=row['remarks'] or '',
                        prescription=row['prescription'] or ''
                    )
                    mr_imported += 1

            self.stdout.write(f"Imported {mr_imported} Medical Records.")

            # 5. Import Appointments (doctor_appointments)
            cursor.execute("SELECT * FROM doctor_appointments")
            app_rows = cursor.fetchall()
            app_imported = 0

            for row in app_rows:
                app_id = int(row['id'])
                doc_obj = DoctorProfile.objects.filter(id=int(row['doctor_id'])).first() if row['doctor_id'] else None
                pat_obj = Patients.objects.filter(id=int(row['patient_id'])).first() if row['patient_id'] else None

                if doc_obj and pat_obj and not Appointments.objects.filter(id=app_id).exists():
                    st = parse_time(row['start_time']) if row['start_time'] else parse_time("09:00:00")
                    ad = parse_date(row['date']) if row['date'] else parse_date("2026-08-01")
                    Appointments.objects.create(
                        id=app_id,
                        doctor=doc_obj,
                        patient=pat_obj,
                        start_time=st,
                        status=row['status'] or 'scheduled',
                        date=ad
                    )
                    app_imported += 1

            self.stdout.write(f"Imported {app_imported} Appointments.")

        conn.close()

        # Reset Postgres / MySQL sequence counters if running on postgresql / mysql
        try:
            db_engine = connection.vendor
            if db_engine == 'postgresql':
                with connection.cursor() as cursor:
                    for table in ['accounts_user', 'doctor_doctorprofile', 'doctor_patients', 'doctor_medicalrecord', 'doctor_appointments']:
                        cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table};")
                self.stdout.write(self.style.SUCCESS("PostgreSQL sequences reset successfully."))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Sequence reset notice: {e}"))

        # Run clinic data migration to link all imported records to clinics
        self.stdout.write(self.style.SUCCESS("Linking imported data to clinic structures..."))
        call_command('migrate_clinic_data')
        self.stdout.write(self.style.SUCCESS("Backup import completed successfully!"))
