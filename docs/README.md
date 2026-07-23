# Imhotep Smart Clinic — Developer Documentation

Welcome to the technical documentation for **Imhotep Smart Clinic**, a modern, multi-tenant healthcare management system built with Django, PostgreSQL/SQLite, and Docker.

This documentation serves as a comprehensive guide for new developers, contributors, system administrators, and maintainers.

---

## 🗺️ Documentation Index

| Section | Description |
| :--- | :--- |
| 🏗️ [System Architecture](file:///Users/karimbassem/code/imhotep_tech/imhotep_smart_clinic/docs/architecture.md) | Clinic-Centric multi-tenancy architecture, database schema, entity relationships, and user roles. |
| 🔑 [Auth & Credentials](file:///Users/karimbassem/code/imhotep_tech/imhotep_smart_clinic/docs/authentication_and_authorization.md) | Email verification, OAuth, automated Clinic Admin creation, and password security. |
| 🛡️ [Admin Portal & Scoping](file:///Users/karimbassem/code/imhotep_tech/imhotep_smart_clinic/docs/admin_portal_and_scoping.md) | Multi-tenant query scoping (`ScopedModelAdmin`), permissions model, and Clinic Admin workspace. |
| 🩺 [Patients & Medical Records](file:///Users/karimbassem/code/imhotep_tech/imhotep_smart_clinic/docs/patient_and_medical_records.md) | Patient creation workflows, clinical notes privacy rules, PDF generation, and clinic branding. |
| 📦 [Data Migration Guide](file:///Users/karimbassem/code/imhotep_tech/imhotep_smart_clinic/docs/data_migration_guide.md) | Legacy production data transition (`migrate_clinic_data`), Docker integration, and migration steps. |
| 🛠️ [Contributing & Setup](file:///Users/karimbassem/code/imhotep_tech/imhotep_smart_clinic/docs/contributing_and_setup.md) | Local environment setup (Docker / standard), running migrations, testing, and contribution guidelines. |

---

## ⚡ Quick Start for New Developers

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.13+ (if running locally without Docker)
- Git

### 2. Running with Docker (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/Imhotep-Tech/imhotep_smart_clinic.git
cd imhotep_smart_clinic

# 2. Copy the environment variables file
cp .env.example .env

# 3. Start the containers
docker-compose up -d --build
```
The application will automatically perform database migrations and execute `migrate_clinic_data` on startup.
- **Web App**: `http://localhost:8000`
- **Django Admin**: `http://localhost:8000/admin/`

---

## 🏛️ System Overview

Imhotep Smart Clinic uses a **Clinic-Centric Multi-Tenancy Architecture**. 

- Each **Clinic** acts as the central entity in the database.
- **Doctors** belong to a Clinic (a Clinic can have 1 or multiple doctors).
- **Assistants** belong to a Clinic and can handle one or more doctors in that Clinic.
- **Patients** belong to a Clinic.
- **Clinic Admins** manage their specific Clinic's records through a strictly scoped Django Admin workspace.
- **Super Admins** manage the global platform across all clinics.

```
                  +-------------------+
                  |    Super Admin    |
                  +---------+---------+
                            |
                   +--------v--------+
                   |     Clinic      |
                   +---+---------+---+
                       |         |
         +-------------+         +------------+
         |                                    |
+--------v--------+                  +--------v--------+
| Doctor Profile  |                  | Assistant Profile|
+--------+--------+                  +--------+--------+
         |                                    |
         +-----------------+------------------+
                           |
                  +--------v--------+
                  | Patients Record |
                  +--------+--------+
                           |
             +-------------+-------------+
             |                           |
    +--------v--------+         +--------v--------+
    | Medical Record  |         |   Appointment   |
    +-----------------+         +-----------------+
```

Read the [Architecture Guide](file:///Users/karimbassem/code/imhotep_tech/imhotep_smart_clinic/docs/architecture.md) for full database schemas and relationships.
