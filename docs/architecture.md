# 🏗️ System Architecture & Data Model

This document outlines the architecture, database models, entity relationships, and access control levels in **Imhotep Smart Clinic**.

---

## 🏛️ Clinic-Centric Multi-Tenancy

The database model is structured around a central **Clinic** entity. Every healthcare entity (Doctors, Assistants, Patients, Medical Records, Appointments) belongs to a `Clinic`.

```
                    +--------------------+
                    |       Clinic       |
                    |--------------------|
                    | id                 |
                    | name               |
                    | address            |
                    | phone_number       |
                    | logo               |
                    | admin (FK -> User) |
                    +---------+----------+
                              |
     +------------------------+------------------------+
     |                        |                        |
+----v---------------+  +-----v---------------+  +-----v---------------+
|   DoctorProfile    |  |  AssistantProfile   |  |      Patients       |
|--------------------|  |---------------------|  |---------------------|
| id                 |  | id                  |  | id                  |
| user (FK)          |  | user (FK)           |  | user (FK, optional) |
| specialization     |  | clinic (FK)         |  | clinic (FK)         |
| clinic (FK)        |  | doctors (M2M)       |  | doctor (FK)         |
+---------+----------+  +---------------------+  +----------+----------+
          |                                                 |
          +------------------------+------------------------+
                                   |
                         +---------v----------+
                         |   MedicalRecord    |
                         |--------------------|
                         | id                 |
                         | clinic (FK)        |
                         | doctor (FK)        |
                         | patient (FK)       |
                         | details (private)  |
                         | remarks (public)   |
                         | prescription (pub) |
                         +--------------------+
```

---

## 👥 User Roles & Permissions Matrix

The custom `User` model (`accounts/models.py`) supports 5 primary roles specified by `user_type`:

| Role (`user_type`) | Description | Permissions & Workspace |
| :--- | :--- | :--- |
| **`super_admin`** | System Super Administrator | Unrestricted platform access across all clinics via Django Admin. |
| **`clinic_admin`** | Clinic Administrator | Managed access via Django Admin scoped strictly to their Clinic's records. |
| **`doctor`** | Medical Doctor | Doctor Dashboard (`/doctor/dashboard/`). Full clinical access to patients, prescriptions, and private notes in their clinic. |
| **`assistant`** | Medical Assistant | Assistant Dashboard (`/assistant/dashboard/`). Manages appointments and patients for assigned doctors in their clinic. |
| **`patient`** | Patient Account | Patient View. Access to personal appointment bookings, prescriptions, and remarks (clinical notes hidden). |

---

## 🗄️ Core Data Schemas

### 1. `Clinic` Model (`doctor/models.py`)
Central model representing a medical clinic unit.
- `name`: Clinic title (e.g. *"Dr. Smith's Clinic"*).
- `address`: Physical location.
- `phone_number`: Primary phone contact.
- `logo`: Path to the uploaded clinic branding image (`clinic_logos/...`).
- `admin`: ForeignKey to `User` (`user_type='clinic_admin'`).

### 2. `DoctorProfile` Model (`doctor/models.py`)
- `user`: OneToOne link to `User` (`user_type='doctor'`).
- `specialization`: Medical specialization field.
- `clinic`: ForeignKey to `Clinic` (each doctor belongs to 1 clinic; a clinic can have multiple doctors).
- `logo_path` (Property): Backwards-compatible lookup returning `self.clinic.logo` if set.

### 3. `AssistantProfile` Model (`assistant/models.py`)
- `user`: OneToOne link to `User` (`user_type='assistant'`).
- `clinic`: ForeignKey to `Clinic`.
- `doctors`: ManyToManyField to `DoctorProfile` (an assistant can handle 1 or more doctors within their clinic).

### 4. `Patients` Model (`doctor/models.py`)
- `user`: ForeignKey to `User` (`user_type='patient'`, optional for doctor-created patients).
- `clinic`: ForeignKey to `Clinic`.
- `doctor`: ForeignKey to `DoctorProfile` (primary doctor).
- `name`, `phone_number`, `gender`, `date_of_birth`: Demographic information.

### 5. `MedicalRecord` Model (`doctor/models.py`)
- `clinic`: ForeignKey to `Clinic`.
- `doctor`: ForeignKey to `DoctorProfile`.
- `patient`: ForeignKey to `Patients`.
- `details`: **Private Clinical Notes** (visible ONLY to Doctor & Assistant).
- `remarks`: **General Remarks** (visible to Patient).
- `prescription`: **Medication & Instructions** (visible to Patient & printable as PDF).
