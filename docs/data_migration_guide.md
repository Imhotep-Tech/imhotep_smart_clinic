# 📦 Production Data Migration Guide

This document explains how to migrate existing production databases to the new **Clinic-Centric Architecture**.

---

## 🚀 Overview

The system includes an automated, idempotent management command (`python manage.py migrate_clinic_data`) to transition legacy single-doctor records into multi-tenant Clinic structures.

It is automatically executed on container startup via `entrypoint.sh`.

---

## 🛠️ Management Command Execution

You can run the migration command manually on any server or Docker environment:

```bash
# Docker environment
docker-compose exec backend python manage.py migrate_clinic_data

# Local environment
python manage.py migrate_clinic_data
```

---

## 🔄 What the Migration Command Does (`migrate_clinic_data.py`)

The command executes inside an atomic database transaction (`transaction.atomic()`):

### Step 1: Migrate Doctors, Clinics & Logos
- Iterates over all `DoctorProfile` records.
- If a doctor does not have a `Clinic`, creates a default Clinic: `"Dr. [Name]'s Clinic"`.
- Copies legacy doctor logo paths (`doc.clinic_photo_path`) into `Clinic.logo` if `Clinic.logo` is empty.
- Links `doc.clinic = clinic`.

### Step 2: Migrate Patients
- Iterates over all `Patients` records.
- If a patient has a `doctor` but no `clinic`, sets `patient.clinic = patient.doctor.clinic`.

### Step 3: Migrate Assistants & Multi-Doctor Bindings
- Iterates over all `AssistantProfile` records.
- If an assistant has a primary `doctor` but no `clinic`, sets `assistant.clinic = assistant.doctor.clinic`.
- Binds existing `assistant.doctor` to the `doctors` ManyToMany relationship (`assistant.doctors.add(assistant.doctor)`).

### Step 4: Migrate Medical Records & Appointments
- Iterates over all `MedicalRecord` and `Appointments` entries without a `clinic` set.
- Populates `rec.clinic = rec.doctor.clinic` and `app.clinic = app.doctor.clinic`.

---

## 🐳 Docker Integration (`entrypoint.sh`)

The migration step is embedded directly into `entrypoint.sh` before launching Gunicorn / Django dev server:

```bash
#!/bin/bash
set -e

echo "Checking for migration conflicts..."
python manage.py makemigrations --check || {
    echo "Migration conflicts detected! Generating new migrations..."
    python manage.py makemigrations
}

echo "Running database migrations..."
python manage.py migrate

echo "Migrating clinic data structure..."
python manage.py migrate_clinic_data

exec "$@"
```
