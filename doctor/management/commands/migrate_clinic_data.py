from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User
from doctor.models import Clinic, DoctorProfile, Patients, MedicalRecord, Appointments
from assistant.models import AssistantProfile

class Command(BaseCommand):
    help = 'Migrates production data so every doctor, patient, assistant, medical record, and appointment is correctly linked to a Clinic and Doctor.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting clinic data migration..."))

        # Safety check: ensure doctor_doctorprofile exists and has clinic_id column
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                table_names = connection.introspection.table_names(cursor)
                if 'doctor_doctorprofile' not in table_names:
                    self.stdout.write(self.style.WARNING("doctor_doctorprofile table does not exist yet. Please run 'python manage.py migrate' first."))
                    return

                columns = [col[0] for col in connection.introspection.get_table_description(cursor, 'doctor_doctorprofile')]
                if 'clinic_id' not in columns:
                    self.stdout.write(self.style.WARNING("clinic_id column does not exist on doctor_doctorprofile yet. Please run 'python manage.py migrate' first."))
                    return
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Database introspection notice: {e}"))

        with transaction.atomic():
            # 0. Ensure DoctorProfile exists for all doctor Users
            doctor_users = User.objects.filter(user_type='doctor')
            for d_user in doctor_users:
                DoctorProfile.get_or_create_for_user(d_user)

            # 1. Migrate Doctors & Clinics & Logos
            doctors = DoctorProfile.objects.all()
            clinic_created_count = 0
            doctor_updated_count = 0
            logos_migrated_count = 0

            from django.db.models import Count
            primary_doctor = DoctorProfile.objects.filter(user__username='amir').first() or DoctorProfile.objects.annotate(num_p=Count('doctor_patients')).order_by('-num_p').first() or doctors.first()
            primary_clinic = primary_doctor.clinic if (primary_doctor and primary_doctor.clinic) else Clinic.objects.first()

            for doc in doctors:
                if not doc.clinic:
                    doc_name = doc.user.get_full_name() or doc.user.username
                    clinic, created = Clinic.objects.get_or_create(
                        name=f"Dr. {doc_name}'s Clinic",
                        defaults={
                            'address': '',
                            'phone_number': '',
                            'logo': doc.clinic_photo_path or '',
                            'admin': doc.user
                        }
                    )
                    if created:
                        clinic_created_count += 1
                    doc.clinic = clinic
                    doc.save()
                    doctor_updated_count += 1

                if not primary_clinic and doc.clinic:
                    primary_clinic = doc.clinic

                # Copy clinic photo path to clinic.logo if clinic logo is empty
                if doc.clinic_photo_path and doc.clinic and not doc.clinic.logo:
                    doc.clinic.logo = doc.clinic_photo_path
                    doc.clinic.save()
                    logos_migrated_count += 1

            self.stdout.write(f"Created {clinic_created_count} clinics, linked {doctor_updated_count} doctors, migrated {logos_migrated_count} clinic logos.")

            # 2. Migrate Existing Patients Records
            patients = Patients.objects.all()
            patients_updated = 0

            for patient in patients:
                updated = False
                if not patient.clinic and patient.doctor and patient.doctor.clinic:
                    patient.clinic = patient.doctor.clinic
                    updated = True
                elif patient.clinic and not patient.doctor:
                    first_doc = patient.clinic.doctors.first() or primary_doctor
                    if first_doc:
                        patient.doctor = first_doc
                        updated = True
                elif not patient.clinic and not patient.doctor:
                    if primary_clinic:
                        patient.clinic = primary_clinic
                    if primary_doctor:
                        patient.doctor = primary_doctor
                    updated = True

                if updated:
                    patient.save()
                    patients_updated += 1

            # 2b. Auto-create Patients profile records for patient User accounts missing one
            patient_users_without_profile = User.objects.filter(user_type='patient', patient_profile__isnull=True)
            auto_created_patients = 0

            for p_user in patient_users_without_profile:
                p_name = p_user.get_full_name() or p_user.username
                Patients.objects.create(
                    user=p_user,
                    clinic=primary_clinic,
                    doctor=primary_doctor,
                    name=p_name,
                    phone_number='',
                    gender='Male'
                )
                auto_created_patients += 1

            self.stdout.write(f"Updated {patients_updated} patient records, auto-created {auto_created_patients} missing patient profiles.")

            # 3. Migrate Assistants
            assistants = AssistantProfile.objects.all()
            assistants_updated = 0

            for assistant in assistants:
                updated = False
                if assistant.doctor:
                    if not assistant.clinic and assistant.doctor.clinic:
                        assistant.clinic = assistant.doctor.clinic
                        updated = True
                    if assistant.doctor not in assistant.doctors.all():
                        assistant.doctors.add(assistant.doctor)
                        updated = True
                elif not assistant.clinic and primary_clinic:
                    assistant.clinic = primary_clinic
                    updated = True

                if updated:
                    assistant.save()
                    assistants_updated += 1

            self.stdout.write(f"Updated {assistants_updated} assistant profiles.")

            # 4. Migrate Medical Records
            medical_records = MedicalRecord.objects.filter(clinic__isnull=True)
            mr_count = 0
            for record in medical_records:
                if record.doctor and record.doctor.clinic:
                    record.clinic = record.doctor.clinic
                    record.save()
                    mr_count += 1
                elif record.patient and record.patient.clinic:
                    record.clinic = record.patient.clinic
                    record.save()
                    mr_count += 1
                elif primary_clinic:
                    record.clinic = primary_clinic
                    record.save()
                    mr_count += 1

            self.stdout.write(f"Updated {mr_count} medical records with clinic links.")

            # 5. Migrate Appointments
            appointments = Appointments.objects.filter(clinic__isnull=True)
            app_count = 0
            for app in appointments:
                if app.doctor and app.doctor.clinic:
                    app.clinic = app.doctor.clinic
                    app.save()
                    app_count += 1
                elif app.patient and app.patient.clinic:
                    app.clinic = app.patient.clinic
                    app.save()
                    app_count += 1
                elif primary_clinic:
                    app.clinic = primary_clinic
                    app.save()
                    app_count += 1

            self.stdout.write(f"Updated {app_count} appointments with clinic links.")

        self.stdout.write(self.style.SUCCESS("Clinic data migration completed successfully!"))

