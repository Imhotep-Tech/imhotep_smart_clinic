# 🛠️ Contributing & Setup Guide

This guide provides instructions for setting up your local environment, running tests, following coding standards, and contributing to **Imhotep Smart Clinic**.

---

## 💻 Local Development Setup

### Option A: Running with Docker (Recommended)

1. Clone the codebase and create environment configuration:
   ```bash
   cp .env.example .env
   ```

2. Build and start services:
   ```bash
   docker-compose up --build
   ```

3. Access application:
   - Web App: `http://localhost:8000`
   - Django Admin: `http://localhost:8000/admin/`

---

### Option B: Running Standalone (Python Virtual Environment)

1. Create and activate a Python 3.13 virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env` (or default to SQLite):
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   SITE_DOMAIN=127.0.0.1:8000
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   python manage.py migrate_clinic_data
   ```

5. Start local server:
   ```bash
   python manage.py runserver
   ```

---

## 📐 Coding Standards & Guidelines

### 1. Translation Function Shadowing
**Crucial Rules for Django i18n**:
When using `from django.utils.translation import gettext_lazy as _`, **never** use `_` as a throwaway variable in tuple unpacking (e.g. `obj, _ = Model.objects.get_or_create(...)`).
Doing so overwrites the `_` translation function with a boolean value, causing runtime `TypeError: 'bool' object is not callable` exceptions.
- **Incorrect**: `clinic, _ = Clinic.objects.get_or_create(...)`
- **Correct**: `clinic, _created = Clinic.objects.get_or_create(...)`

### 2. Multi-Tenant Scoping
- All model querysets in views and admin classes must filter by `clinic` (e.g. `filter(clinic=current_user_clinic)`).
- Admin classes must inherit from `ScopedModelAdmin` to preserve data isolation.

### 3. Template Strings & Translation Tags
- In `{% trans "..." %}` tags, avoid using inner double quotes. Use single quotes inside translation strings (e.g. `{% trans "Terms of 'Services'" %}`) to prevent Django `TemplateSyntaxError` parser failures.

---

## 🧪 Testing & Verification

Run system checks and Django tests:
```bash
python manage.py check
python manage.py test
```

---

## 📩 Submitting Contributions

1. Create a descriptive feature branch (`git checkout -b feature/clinic-analytics`).
2. Verify all migrations run cleanly (`python manage.py makemigrations --check`).
3. Ensure no system check errors (`python manage.py check`).
4. Commit your changes and submit a Pull Request.
