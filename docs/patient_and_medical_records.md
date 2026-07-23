# 🩺 Patients & Medical Records

This document explains patient creation options, privacy boundaries for clinical notes, PDF prescription rendering, and clinic branding.

---

## 👥 Two Methods for Adding Patients

Imhotep Smart Clinic supports two workflows for adding patients:

### Method 1: Doctor / Assistant Direct Addition (with Password)
- **Location**: `doctor/patients.py` (`add_patient`)
- **Workflow**:
  1. A doctor or assistant fills out the patient registration form in the dashboard.
  2. The form includes an optional **Password** field.
  3. If a password is provided, the system automatically creates a `User` account (`user_type='patient'`, `email_verify=True`) and links `patient.user = user`.
  4. The patient can log in immediately to view their prescriptions and appointments.

### Method 2: Patient Self-Registration & Appointment Booking
- **Workflow**:
  1. Patient accesses the public booking / signup interface.
  2. Patient creates their user account (`user_type='patient'`) and books an appointment.
  3. The doctor or assistant can subsequently update the patient's record and add medical details.

---

## 🔒 Medical Record Privacy Rules

Medical records contain sensitive health information. Access rights are strictly partitioned:

| Record Field | Visible To Doctor | Visible To Assistant | Visible To Patient |
| :--- | :---: | :---: | :---: |
| **`details` (Clinical Notes)** | ✅ **Yes** | ✅ **Yes** | ❌ **Hidden** |
| **`remarks` (General Remarks)** | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** |
| **`prescription` (Medications)** | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** |

### Implementation Detail
In the Patient View template (`patient/templates/...`), the `details` field is omitted from rendering to ensure clinical diagnostic notes remain private to healthcare providers.

---

## 📄 PDF Prescriptions & Clinic Logo Integration

When a doctor generates a PDF prescription (`doctor/medical_records.py` -> `render_to_pdf`):

1. **Logo Field**: Logos are stored directly on the central `Clinic.logo` model field.
2. **Backwards Compatibility**: `DoctorProfile.logo_path` property resolves `self.clinic.logo` or legacy paths seamlessly:
   ```python
   @property
   def logo_path(self):
       if self.clinic and self.clinic.logo:
           return self.clinic.logo
       return self.clinic_photo_path or ""
   ```
3. **PDF Generator**: Fetches `doctor_profile.logo_path` and resolves absolute media filesystem paths for PDF engine inclusion.
