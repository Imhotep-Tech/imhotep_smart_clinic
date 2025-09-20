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

- **User Management**: Role-based access control for doctors, and assistants
- **Patient Records**: Maintain detailed digital medical records
- **Prescription Management**: Create and generate PDF prescriptions
- **Dashboard Analytics**: Get insights into your practice
- **Progressive Web App**: Can be installed on mobile devices
- **Responsive Design**: Works on all device sizes
- **Multilingual Support**: Includes support for Arabic text in prescriptions

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- Docker and Docker Compose (optional, for containerized setup)
- Git

### Setup

#### Using Docker (Recommended)

1. Clone the repository
```bash
git clone https://github.com/imhotep-tech/imhotep_smart_clinic.git
cd imhotep_smart_clinic
```

2. Copy the environment file
```bash
cp .env.example .env
# Edit .env file with your settings
```

3. Build and start the Docker containers
```bash
docker-compose up --build
```

4. Run migrations inside the container
```bash
docker-compose exec web python manage.py migrate
```

5. Create a superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

6. Access the application at [http://localhost:8000](http://localhost:8000)

#### Manual Setup

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

#### Using Docker
```bash
docker-compose exec web python manage.py test
```

#### Without Docker
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

Contributions are welcome! Follow these steps to get started:

1. Fork the repository on GitHub.
2. Clone your forked repository locally:
   ```bash
   git clone https://github.com/<your-username>/imhotep_smart_clinic.git
   cd imhotep_smart_clinic
   ```
3. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add your commit message here"
   ```
5. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Open a pull request on the main repository.

### Setting Up for Development

#### Using Docker
Follow the [Docker setup](#using-docker-recommended) instructions to get started quickly.

#### Without Docker
Follow the [manual setup](#manual-setup) instructions.

Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## Security

Please report security vulnerabilities according to our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Tailwind CSS](https://tailwindcss.com/)
- [Django](https://www.djangoproject.com/)
- [WeasyPrint](https://weasyprint.org/) for PDF generation
- All our [contributors](https://github.com/imhotep-tech/imhotep_smart_clinic/graphs/contributors)
