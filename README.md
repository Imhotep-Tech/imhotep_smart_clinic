# Imhotep Smart Clinic

<p align="center">
  <img src="static/imhotep_clinic.png" alt="Imhotep Smart Clinic Logo" width="200">
</p>

<p align="center">
  A modern medical clinic management system built with Django and TailwindCSS
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#development">Development</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

## Features

Imhotep Smart Clinic provides a comprehensive solution for medical practice management:

- **User Management**: Role-based access control for doctors, assistants, and patients
- **Patient Records**: Maintain detailed digital medical records
- **Prescription Management**: Create and generate PDF prescriptions
- **Dashboard Analytics**: Get insights into your practice
- **Progressive Web App**: Works offline and can be installed on mobile devices
- **Responsive Design**: Works on all device sizes
- **Multilingual Support**: Includes support for Arabic text in prescriptions

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- Git

### Setup

1. Clone the repository
```bash
git clone https://github.com/imhotep-tech/imhotep_smart_clinic.git
cd imhotep_smart_clinic
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env file with your settings
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create a superuser
```bash
python manage.py createsuperuser
```

7. Start the development server
```bash
python manage.py runserver
```

8. Visit http://localhost:8000 in your browser

## Usage

### Doctor Portal

The doctor portal allows physicians to:
- View their dashboard with analytics
- Manage patient records and medical histories
- Create detailed prescriptions with rich text formatting
- Generate PDF prescriptions
- Manage assistants and staff

### Assistant Portal

Assistants can:
- View assigned patients
- Update patient contact details
- Schedule appointments
- Manage day-to-day clinic operations

### PWA Features

The application supports Progressive Web App features:
- Installation on mobile devices

## Development

### Project Structure

```
imhotep_smart_clinic/
├── accounts/             # User authentication and profiles
├── assistant/            # Assistant-specific functionality
├── doctor/               # Doctor-specific functionality
├── static/               # Static files (JS, CSS, images)
├── templates/            # Base HTML templates
└── imhotep_smart_clinic/ # Project settings
```

### Running Tests

```bash
python manage.py test
```

### Building Frontend Assets

The project uses TailwindCSS served via CDN for development. For production:

```bash
# Install Node.js dependencies
npm install

# Build production CSS
npm run build:css
```

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## Security

Please report security vulnerabilities according to our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Tailwind CSS](https://tailwindcss.com/)
- [Django](https://www.djangoproject.com/)
- [WeasyPrint](https://weasyprint.org/) for PDF generation
- All our [contributors](https://github.com/imhotep-tech/imhotep_smart_clinic/graphs/contributors)
