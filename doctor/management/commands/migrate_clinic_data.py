from django.core.management.base import BaseCommand
from django.db import transaction
from doctor.models import Clinic, DoctorProfile, Patients, MedicalRecord, Appointments
from assistant.models import AssistantProfile

class Command(BaseCommand):
    help = 'Migrates production data so every doctor, patient, assistant, medical record, and appointment is correctly linked to a Clinic.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting clinic data migration..."))

        with transaction.atomic():
            # 1. Migrate Doctors & Clinics & Logos
            doctors = DoctorProfile.objects.all()
            clinic_created_count = 0
            doctor_updated_count = 0
            logos_migrated_count = 0

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

                # Copy clinic photo path to clinic.logo if clinic logo is empty
                if doc.clinic_photo_path and doc.clinic and not doc.clinic.logo:
                    doc.clinic.logo = doc.clinic_photo_path
                    doc.clinic.save()
                    logos_migrated_count += 1

            self.stdout.write(f"Created {clinic_created_count} clinics, linked {doctor_updated_count} doctors, migrated {logos_migrated_count} clinic logos.")

            # 2. Migrate Patients
            patients = Patients.objects.all()
            patients_updated = 0

            for patient in patients:
                updated = False
                if not patient.clinic and patient.doctor and patient.doctor.clinic:
                    patient.clinic = patient.doctor.clinic
                    updated = True
                elif patient.clinic and not patient.doctor:
                    first_doc = patient.clinic.doctors.first()
                    if first_doc:
                        patient.doctor = first_doc
                        updated = True
                if updated:
                    patient.save()
                    patients_updated += 1

            self.stdout.write(f"Updated {patients_updated} patient records.")

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

            self.stdout.write(f"Updated {app_count} appointments with clinic links.")

        self.stdout.write(self.style.SUCCESS("Clinic data migration completed successfully!"))
