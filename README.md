# Imhotep Smart Clinic

<p align="center">
  <img src="static/imhotep_clinic.png" alt="Imhotep Smart Clinic Logo" width="200">
</p>

<p align="center">
  <strong>A Self-Hostable Medical Clinic Management System</strong>
</p>

<p align="center">
  Built with Django, TailwindCSS, and designed for easy self-hosting
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#installation">Installation</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#usage">Usage</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#troubleshooting">Troubleshooting</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## 🏥 What is Imhotep Smart Clinic?

Imhotep Smart Clinic is a **fully self-hostable**, open-source medical clinic management system designed for doctors and medical practices who want complete control over their patient data and clinic operations. Built with modern web technologies, it provides a comprehensive solution for managing patients, prescriptions, appointments, and medical records.

### Why Self-Hosting?

- **Complete Data Ownership**: Your patient data stays on your servers
- **Privacy Compliant**: Meet local data protection regulations (HIPAA, GDPR, etc.)
- **Cost Effective**: No monthly subscription fees
- **Customizable**: Modify the system to fit your clinic's workflow
- **No Vendor Lock-in**: Your data is always accessible

## ✨ Features

### 👨‍⚕️ Doctor Portal
Located at: `/doctor/`

- **Dashboard Analytics**
  - Patient statistics and growth trends
  - Recent activity overview
  - Quick access to pending tasks
  - Visual charts and graphs

- **Patient Management** (`/doctor/patients/`)
  - Complete patient registry
  - Detailed medical histories
  - Patient search and filtering
  - Add/edit/delete patient records
  - Track patient visits and outcomes

- **Prescription System** (`/doctor/prescriptions/`)
  - Rich text prescription editor
  - Support for Arabic and English text
  - PDF generation with custom branding
  - Prescription templates
  - Print and download prescriptions
  - Prescription history tracking

- **Assistant Management** (`/doctor/assistants/`)
  - Invite and manage clinic assistants
  - Assign roles and permissions
  - Monitor assistant activity

### 👨‍💼 Assistant Portal
Located at: `/assistant/`

- **Patient Operations**
  - View assigned patient list
  - Update patient contact information
  - Schedule and manage appointments
  - Add patient notes and updates

- **Daily Operations**
  - Appointment calendar
  - Patient check-in/check-out
  - Task management

### 🔐 Authentication & User Management
Located at: `/accounts/`

- **User Registration** (`/accounts/register/`)
  - Email-based registration
  - Role selection (Doctor/Assistant)
  - Email verification (if configured)

- **Login Options** (`/accounts/login/`)
  - Standard email/password login
  - Google OAuth integration (optional)
  - "Remember me" functionality

- **Profile Management** (`/accounts/profile/`)
  - Update personal information
  - Change password
  - Manage clinic details (doctors only)

- **Password Recovery** (`/accounts/password-reset/`)
  - Email-based password reset
  - Secure token generation

### 📱 Progressive Web App (PWA)
- **Install on Mobile**: Add to home screen on iOS/Android
- **Offline Capability**: Basic functionality works offline
- **Responsive Design**: Works on desktop, tablet, and mobile
- **App-like Experience**: Native app feel on mobile devices

### 🌐 Multilingual Support
- **Arabic Support**: Full RTL support for Arabic prescriptions
- **English Interface**: Default English UI
- **Easy Translation**: i18n ready for additional languages

### 📄 PDF Generation
- **Professional Prescriptions**: Generate branded PDF prescriptions
- **WeasyPrint Integration**: High-quality PDF rendering
- **Custom Templates**: Customize prescription layout
- **Print Ready**: Optimized for A4 printing

## 🚀 Quick Start

### Using Docker (Recommended for Production)

```bash
# 1. Clone the repository
git clone https://github.com/Imhotep-Tech/imhotep_smart_clinic.git
cd imhotep_smart_clinic

# 2. Create your configuration file
cp .env.example .env
# Edit .env with your settings (see Configuration section)

# 3. Start the application
docker-compose up -d

# 4. Access your clinic at http://localhost:8000
```

### Using Python (Development)

```bash
# 1. Clone the repository
git clone https://github.com/Imhotep-Tech/imhotep_smart_clinic.git
cd imhotep_smart_clinic

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Set up database
python manage.py migrate
python manage.py createsuperuser

# 6. Start development server
python manage.py runserver

# 7. Access at http://localhost:8000
```

## 📦 Installation

### Prerequisites

- **For Docker Setup**:
  - Docker Engine 20.10+
  - Docker Compose 1.29+
  - 2GB RAM minimum, 4GB recommended
  - 10GB free disk space

- **For Manual Setup**:
  - Python 3.8 or higher (3.10+ recommended)
  - pip 21.0+
  - PostgreSQL 12+ (optional, SQLite works for development)
  - Node.js 14+ (optional, for frontend development)
  - 2GB RAM minimum, 4GB recommended

### Detailed Installation Steps

#### Option 1: Docker Deployment (Production Ready)

**Step 1: Prepare Your Server**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

**Step 2: Clone and Configure**

```bash
# Clone the repository
git clone https://github.com/Imhotep-Tech/imhotep_smart_clinic.git
cd imhotep_smart_clinic

# Create environment file
cp .env.example .env

# Edit configuration (see Configuration section)
nano .env  # or use your preferred editor
```

**Step 3: Launch Application**

```bash
# Build and start containers
docker-compose up -d --build

# Wait for containers to be healthy
docker-compose ps

# Collect static files (for production)
docker-compose exec web python manage.py collectstatic --no-input
```

**Step 4: Verify Installation**

```bash
# Check application logs
docker-compose logs -f web

# Access the application
# Open http://your-server-ip:8000 in your browser
```

#### Option 2: Manual Installation

**Step 1: Install System Dependencies**

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib
sudo apt install libpq-dev python3-dev  # For PostgreSQL
sudo apt install libcairo2 libpango-1.0-0 libpangocairo-1.0-0  # For PDF generation

# For macOS
brew install python postgresql cairo pango gdk-pixbuf libffi
```

**Step 2: Set Up PostgreSQL (Optional)**

```bash
# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE imhotepclinic_db;
postgres=# CREATE USER imhotepclinic_user WITH PASSWORD 'your_secure_password';
postgres=# ALTER ROLE imhotepclinic_user SET client_encoding TO 'utf8';
postgres=# ALTER ROLE imhotepclinic_user SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE imhotepclinic_user SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE imhotepclinic_db TO imhotepclinic_user;
postgres=# \q
```

**Step 3: Set Up Python Environment**

```bash
# Clone repository
git clone https://github.com/Imhotep-Tech/imhotep_smart_clinic.git
cd imhotep_smart_clinic

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4: Configure Application**

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env

# Update these minimum settings:
# - SECRET_KEY: Generate a new one
# - DEBUG: Set to False for production
# - database_type: 'postgresql' or 'sqlite'
# - DATABASE_* settings if using PostgreSQL
# - SITE_DOMAIN: Your domain or IP
```

**Step 5: Initialize Database**

```bash
# Run migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

**Step 6: Run Application**

```bash
# Development server
python manage.py runserver 0.0.0.0:8000

# For production, use Gunicorn
pip install gunicorn
gunicorn imhotep_smart_clinic.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## ⚙️ Configuration

### Environment Variables Explained

Create a `.env` file by copying `.env.example` and configure the following:

#### Application Settings

```bash
# DEBUG: Enable detailed error pages
# Set to False in production!
DEBUG=True

# SECRET_KEY: Django secret key for cryptographic signing
# Generate a new one: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY='your-secret-key-here'

# SITE_DOMAIN: Your clinic's domain or IP address
# Used for OAuth callbacks and email links
# Examples:
#   Development: http://localhost:8000
#   Production: https://clinic.example.com
SITE_DOMAIN='http://localhost:8000'
```

#### Database Configuration

```bash
# database_type: Choose your database backend
# Options: 'postgresql' (recommended for production), 'sqlite' (development only)
database_type='postgresql'

# PostgreSQL Settings (only if database_type='postgresql')
DATABASE_NAME='imhotepclinic_db'
DATABASE_USER='imhotepclinic_user'
DATABASE_PASSWORD='strong_password_here'
DATABASE_HOST='localhost'  # Use 'db' for Docker, 'localhost' for local PostgreSQL

# SQLite: No configuration needed, file created automatically
```

#### Google OAuth (Optional)

```bash
# To enable Google Sign-In:
# 1. Go to https://console.cloud.google.com/
# 2. Create a new project or select existing
# 3. Enable Google+ API
# 4. Create OAuth 2.0 credentials
# 5. Add authorized redirect URI: {SITE_DOMAIN}/accounts/google/callback/

GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-client-secret'

# Leave empty to disable Google login
```

#### Email Configuration (Optional)

```bash
# Email settings for password reset and notifications
# Leave empty to disable email features

# For Gmail:
MAIL_USER='your-email@gmail.com'
MAIL_PASSWORD='your-app-password'  # Not your regular password!

# Generate Gmail App Password:
# 1. Enable 2-Factor Authentication
# 2. Visit https://myaccount.google.com/apppasswords
# 3. Generate app password for "Mail"

# For other SMTP servers, you may need to modify settings.py
```

### Production Configuration Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate and set a strong `SECRET_KEY`
- [ ] Configure `SITE_DOMAIN` to your actual domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong database passwords
- [ ] Configure email settings for notifications
- [ ] Set up HTTPS/SSL (highly recommended for medical data)
- [ ] Configure regular database backups
- [ ] Set up firewall rules
- [ ] Enable logging and monitoring

### Setting Up HTTPS (Production)

For production deployments, use a reverse proxy like Nginx with Let's Encrypt:

```bash
# Install Nginx and Certbot
sudo apt install nginx certbot python3-certbot-nginx

# Configure Nginx (example configuration)
sudo nano /etc/nginx/sites-available/clinic

# Add SSL certificate
sudo certbot --nginx -d your-domain.com
```

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/imhotep_smart_clinic/staticfiles/;
    }

    location /media/ {
        alias /path/to/imhotep_smart_clinic/media/;
    }
}
```

## 📖 Usage Guide

### First-Time Setup

1. **Access the Application**
   - Navigate to `http://your-domain:8000`
   - You'll see the landing page

2. **Create Your Account**
   - Click "Register" (`/accounts/register/`)
   - Choose role: "Doctor" for clinic owner
   - Fill in your details
   - Verify email if configured

3. **Complete Your Profile**
   - Log in and go to Profile (`/accounts/profile/`)
   - Add clinic information
   - Upload profile picture
   - Set your specialization

4. **Add Your First Patient**
   - Go to Doctor Portal → Patients (`/doctor/patients/`)
   - Click "Add New Patient"
   - Fill in patient details
   - Save the record

5. **Create a Prescription**
   - Select a patient
   - Click "New Prescription" (`/doctor/prescriptions/create/`)
   - Use the rich text editor for prescription details
   - Add medications, dosages, instructions
   - Save and generate PDF

### Doctor Workflow

```
1. Log in to Doctor Portal (/doctor/)
   ↓
2. View Dashboard
   - Check today's appointments
   - Review patient statistics
   ↓
3. Manage Patients (/doctor/patients/)
   - Add new patients
   - Update medical histories
   - Review past visits
   ↓
4. Create Prescriptions (/doctor/prescriptions/)
   - Select patient
   - Write prescription
   - Generate PDF
   - Print or email to patient
   ↓
5. Manage Staff (/doctor/assistants/)
   - Invite assistants
   - Assign permissions
```

### Assistant Workflow

```
1. Log in to Assistant Portal (/assistant/)
   ↓
2. View Today's Schedule
   - Check appointments
   - Patient check-ins
   ↓
3. Manage Patients (/assistant/patients/)
   - Update contact info
   - Schedule appointments
   - Add notes
   ↓
4. Support Doctor
   - Prepare patient files
   - Handle administrative tasks
```

### Mobile/PWA Usage

1. **Install on Mobile**
   - Open app in mobile browser
   - Tap "Add to Home Screen" (iOS) or "Install" (Android)
   - App icon appears on home screen

2. **Use Offline**
   - Basic viewing works without internet
   - Sync when connection restored

## 🏗️ Architecture

### Project Structure

```
imhotep_smart_clinic/
├── accounts/                    # User authentication & profiles
│   ├── models.py               # User, Profile models
│   ├── views.py                # Login, register, profile views
│   ├── forms.py                # User forms
│   └── templates/accounts/     # Auth templates
│
├── doctor/                      # Doctor portal
│   ├── models.py               # Patient, Prescription models
│   ├── views.py                # Doctor dashboard, patient management
│   ├── forms.py                # Patient, prescription forms
│   ├── urls.py                 # Doctor routes
│   └── templates/doctor/       # Doctor templates
│
├── assistant/                   # Assistant portal
│   ├── views.py                # Assistant dashboard
│   ├── urls.py                 # Assistant routes
│   └── templates/assistant/    # Assistant templates
│
├── static/                      # Static files
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   ├── images/                 # Images and logos
│   ├── manifest.json           # PWA manifest
│   └── serviceworker.js        # PWA service worker
│
├── templates/                   # Base templates
│   ├── base.html               # Base layout
│   ├── landing.html            # Landing page
│   └── components/             # Reusable components
│
├── media/                       # User uploads
│   ├── profile_pics/           # Profile pictures
│   └── prescriptions/          # Generated PDFs
│
├── imhotep_smart_clinic/        # Project settings
│   ├── settings.py             # Django settings
│   ├── urls.py                 # URL configuration
│   └── wsgi.py                 # WSGI config
│
├── docker-compose.yml           # Docker configuration
├── Dockerfile                   # Docker image definition
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── manage.py                   # Django management script
└── README.md                   # This file
```

### Technology Stack

- **Backend**: Django 4.2+ (Python web framework)
- **Database**: PostgreSQL 12+ (production) or SQLite (development)
- **Frontend**: TailwindCSS 3.0+, Alpine.js
- **PDF Generation**: WeasyPrint (HTML to PDF)
- **Authentication**: Django Auth + Google OAuth
- **PWA**: Service Workers, Web Manifest
- **Deployment**: Docker, Docker Compose, Gunicorn

### Database Schema

**Key Models:**

- **User** (Django built-in): Authentication
- **Profile** (accounts): User profiles, clinic info
- **Patient** (doctor): Patient records
- **MedicalHistory** (doctor): Patient medical histories
- **Prescription** (doctor): Prescriptions
- **Appointment** (doctor): Appointments

## 🔧 Troubleshooting

### Common Issues

#### 1. Can't connect to database

**Error**: `django.db.utils.OperationalError: could not connect to server`

**Solution**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# For Docker, check container status
docker-compose ps

# Verify database credentials in .env
# Ensure DATABASE_HOST matches your setup (localhost or db)
```

#### 2. Static files not loading

**Error**: CSS/JS not loading, 404 errors

**Solution**:
```bash
# Collect static files
python manage.py collectstatic

# For Docker
docker-compose exec web python manage.py collectstatic

# Check STATIC_ROOT and STATIC_URL in settings.py
```

#### 3. PDF generation fails

**Error**: `OSError: cannot load library 'gobject-2.0-0'`

**Solution**:
```bash
# Install system dependencies
# Ubuntu/Debian:
sudo apt install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0

# macOS:
brew install cairo pango gdk-pixbuf libffi

# For Docker, these are included in the image
```

#### 4. Google OAuth not working

**Error**: Redirect URI mismatch

**Solution**:
```bash
# Ensure SITE_DOMAIN in .env matches your actual domain
SITE_DOMAIN='https://your-actual-domain.com'

# Add this redirect URI in Google Console:
# https://your-actual-domain.com/accounts/google/callback/

# For localhost testing:
# http://localhost:8000/accounts/google/callback/
```

#### 5. Port 8000 already in use

**Error**: `Error: That port is already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python manage.py runserver 0.0.0.0:8080
```

### Getting Help

- **Documentation**: Check this README and inline code comments
- **Issues**: [GitHub Issues](https://github.com/Imhotep-Tech/imhotep_smart_clinic/issues)
- **Security**: See [SECURITY.md](SECURITY.md)

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# For Docker
docker-compose down
docker-compose up -d --build
docker-compose exec web python manage.py migrate

# For manual setup
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

### Database Backups

```bash
# PostgreSQL backup
docker-compose exec db pg_dump -U imhotepclinic_user imhotepclinic_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U imhotepclinic_user imhotepclinic_db < backup_20240101.sql

# For manual PostgreSQL setup
pg_dump -U imhotepclinic_user imhotepclinic_db > backup.sql
psql -U imhotepclinic_user imhotepclinic_db < backup.sql
```

## 🧪 Development

### Code Style

```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black .

# Check style
flake8

# Sort imports
isort .
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Update documentation
4. Commit: `git commit -m "Add: your feature description"`
5. Push: `git push origin feature/your-feature`
6. Create pull request

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**
   - Click "Fork" on GitHub
   - Clone your fork locally

2. **Set Up Development Environment**
   ```bash
   git clone https://github.com/your-username/imhotep_smart_clinic.git
   cd imhotep_smart_clinic
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   python manage.py migrate
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

4. **Make Your Changes**
   - Write clean, documented code
   - Add tests for new features
   - Update documentation

5. **Test Your Changes**
   ```bash
   python manage.py test
   ```

6. **Submit Pull Request**
   - Push to your fork
   - Open PR against `main` branch
   - Describe your changes clearly

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You are free to:
- Use commercially
- Modify
- Distribute
- Private use

Under the condition of:
- Include original license and copyright

## 🔒 Security

**Important Security Notes for Self-Hosting:**

- Always use HTTPS in production
- Keep `DEBUG=False` in production
- Use strong passwords for database and admin accounts
- Regularly update dependencies
- Set up firewall rules
- Enable database backups
- Monitor application logs
- Follow HIPAA/GDPR guidelines for medical data

Report security vulnerabilities privately according to our [Security Policy](SECURITY.md).

## 🙏 Acknowledgements

- [Django Project](https://www.djangoproject.com/) - Web framework
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [WeasyPrint](https://weasyprint.org/) - PDF generation
- [Alpine.js](https://alpinejs.dev/) - JavaScript framework
- All our [contributors](https://github.com/Imhotep-Tech/imhotep_smart_clinic/graphs/contributors)

## 📞 Support

- **Documentation**: This README and code comments
- **Issues**: [GitHub Issues](https://github.com/Imhotep-Tech/imhotep_smart_clinic/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Imhotep-Tech/imhotep_smart_clinic/discussions)

---

<p align="center">
  Made with ❤️ for healthcare professionals who value data ownership and privacy
</p>

<p align="center">
  <strong>100% Self-Hostable • Open Source • Privacy First</strong>
</p>
