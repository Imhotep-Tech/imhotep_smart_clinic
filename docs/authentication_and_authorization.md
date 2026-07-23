# 🔑 Authentication & Authorization

This document details the user registration, email activation, automated Clinic Admin creation, password security, and OAuth flows in **Imhotep Smart Clinic**.

---

## 🔄 User Registration & Activation Flow

```
   [Doctor Sign-Up]
          |
          v
   Create Doctor User
   (user_type='doctor', email_verify=False)
          |
          v
   Create Default Clinic ("Dr. [Name]'s Clinic")
   & DoctorProfile (linked to Clinic)
          |
          v
   Dispatch Activation Email with Token
          |
          v
   Doctor Clicks Activation Link (/activate/uid/token/)
          |
          v
   Verify Token -> Set user.email_verify = True
          |
          v
   Trigger create_and_send_clinic_admin_credentials()
          |
          +--------------------------------------------+
          |                                            |
          v                                            v
Create Clinic Admin User                  Send Credentials Email
(username: admin_<doc_username>,          - Admin Panel URL
 random 12-char password via secrets,      - Admin Username
 user_type='clinic_admin', is_staff=True) - Temp Password
          |
          v
Set clinic.admin = admin_user
```

---

## 🛠️ Automated Clinic Admin Credentials Generation

When a doctor verifies their email address via `/activate/` or registers via Google OAuth, the system executes `create_and_send_clinic_admin_credentials(doctor_user)` in `accounts/auth.py`.

### Implementation Highlights

1. **Unique Username Resolution**:
   - Generates username `admin_<doctor_username>`.
   - If `admin_<doctor_username>` is already taken, appends incremental counters (`admin_john_1`, `admin_john_2`).

2. **Cryptographic Password Generation**:
   - Uses Python's standard `secrets` and `string` modules to generate a 12-character alphanumeric password:
     ```python
     alphabet = string.ascii_letters + string.digits
     random_password = ''.join(secrets.choice(alphabet) for _ in range(12))
     ```
   - Avoids legacy `UserManager` method incompatibilities in Django 5+.

3. **Email Dispatch**:
   - Sends an email containing:
     - **Admin Panel URL**: Derived dynamically from `SITE_DOMAIN/admin/`.
     - **Admin Username**.
     - **Temporary Password**.
     - Instructions to change password upon first login.

---

## 🌐 OAuth Integration (Google Login)

Google OAuth is handled in `add_details_google_login`:
1. User logs in with Google.
2. If account does not exist, prompts user for username and role (`doctor` or `patient`).
3. For doctors:
   - Sets `email_verify = True` (since Google accounts are pre-verified).
   - Auto-creates Clinic and `DoctorProfile`.
   - Immediately calls `create_and_send_clinic_admin_credentials(user)` to email the doctor their Clinic Admin portal credentials.

---

## 🔀 Login Routing Matrix (`accounts/auth.py`)

Upon successful login via `user_login`, users are redirected based on their role:

```python
if request.user.is_doctor():
    return redirect("doctor_dashboard")

if request.user.is_assistant():
    return redirect("assistant_dashboard")

if request.user.is_clinic_admin() or request.user.is_super_admin():
    return redirect("/admin/")

if request.user.is_patient():
    return redirect("patient.dashboard")
```
