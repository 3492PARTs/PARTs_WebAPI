# PARTs WebAPI

Putnam Area Robotics Team Web API - A Django REST Framework application for managing team operations.

## Documentation

📚 **[Complete Documentation Index](docs/README.md)**

### Quick Links
- **[Poetry Setup Guide](docs/POETRY.md)** - Comprehensive guide to using Poetry for dependency management
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to this project
- **[Django Best Practices](DJANGO_BEST_PRACTICES.md)** - Coding standards and patterns
- **[Testing Guide](TESTING.md)** - Testing strategy and coverage roadmap
- **[Test Organization](tests/README.md)** - How tests are organized

### Project History
- **[Reorganization Summary](docs/REORGANIZATION_SUMMARY.md)** - Project structure changes
- **[Refactoring Summary](docs/REFACTORING_SUMMARY.md)** - Code quality improvements

## Project Structure

The project follows Django best practices with a `src/` layout:

```
PARTs_WebAPI/
├── src/
│   ├── parts_webapi/          # Django project package
│   │   ├── settings/          # Split settings
│   │   │   ├── base.py       # Common settings
│   │   │   ├── development.py # Development settings
│   │   │   ├── production.py # Production settings
│   │   │   └── test.py       # Test settings
│   │   ├── urls.py           # URL configuration
│   │   ├── wsgi.py           # WSGI entry point
│   │   └── asgi.py           # ASGI entry point
│   ├── manage.py             # Django management script
│   ├── admin/                # Admin app
│   ├── alerts/               # Alerts app
│   ├── attendance/           # Attendance app
│   ├── form/                 # Form app
│   ├── general/              # General utilities
│   ├── public/               # Public API app
│   ├── scouting/             # Scouting app
│   ├── sponsoring/           # Sponsoring app
│   ├── tba/                  # The Blue Alliance integration
│   └── user/                 # User management app
├── tests/                    # Test suite
├── docs/                     # Documentation
│   ├── README.md            # Documentation index
│   ├── POETRY.md            # Poetry setup guide
│   ├── REORGANIZATION_SUMMARY.md
│   └── REFACTORING_SUMMARY.md
├── templates/                # Django templates
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Poetry configuration
└── README.md                # This file
```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager) - See [Poetry Setup Guide](docs/POETRY.md) for detailed installation and usage

### Installation

1. Clone the repository:
```bash
git clone https://github.com/3492PARTs/PARTs_WebAPI.git
cd PARTs_WebAPI
```

2. Install dependencies using Poetry:
```bash
poetry install --with dev
```

> 📖 **New to Poetry?** Check out our comprehensive [Poetry Setup Guide](docs/POETRY.md) for:
> - Installing Poetry
> - Understanding dependency groups (dev, wvnet, uat)
> - Common commands and workflows
> - Troubleshooting tips

3. Set up environment variables:

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set your values for:
- `SECRET_KEY` - Generate a random string for Django
- `DEBUG` - Set to `True` for development, `False` for production
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Database configuration
- `CLOUDINARY_URL` - Cloudinary configuration for media storage
- `TBA_KEY` - The Blue Alliance API key
- Other optional settings as needed

**Important**: Never commit the `.env` file to version control!

4. Set the Django settings module (for development):
```bash
export DJANGO_SETTINGS_MODULE=parts_webapi.settings.development
```

Or for production:
```bash
export DJANGO_SETTINGS_MODULE=parts_webapi.settings.production
```

**Note**: The default is `parts_webapi.settings.development` if not set.

5. Run migrations:
```bash
cd src
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## Using Different Settings

The project uses split settings for different environments:

- **Development**: `parts_webapi.settings.development`
  - DEBUG=True
  - Uses local database (SQLite by default)
  - Console email backend
  - Allows localhost CORS

- **Production**: `parts_webapi.settings.production`
  - DEBUG=False
  - Enhanced security settings
  - Production-ready CORS and ALLOWED_HOSTS
  - Uses production database

- **Testing**: `parts_webapi.settings.test`
  - Used by pytest
  - In-memory database
  - Simplified authentication

### Setting the Environment

#### Option 1: Environment Variable
```bash
export DJANGO_SETTINGS_MODULE=parts_webapi.settings.development
cd src
python manage.py runserver
```

#### Option 2: Command Line
```bash
cd src
python manage.py runserver --settings=parts_webapi.settings.development
```

#### Option 3: .env File
Set `DJANGO_SETTINGS_MODULE` in your `.env` file:
```
DJANGO_SETTINGS_MODULE=parts_webapi.settings.development
```

## Testing

### Running Tests

Run all tests with coverage:
```bash
poetry run pytest
```

Run tests without coverage (faster for development):
```bash
poetry run pytest --no-cov
```

Run specific test file:
```bash
poetry run pytest tests/general/test_general_security.py
```

Run all tests for a specific app:
```bash
poetry run pytest tests/user/
```

Run tests with verbose output:
```bash
poetry run pytest -v
```

### Coverage Reports

View coverage in terminal:
```bash
poetry run pytest --cov=src --cov-report=term-missing
```

Generate HTML coverage report:
```bash
poetry run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in your browser
```

### Coverage Requirements

This project maintains high test coverage. All pull requests should maintain or improve test coverage:
- The CI pipeline will fail if coverage drops significantly
- Add tests for any new code you write
- Update tests when modifying existing code

### Writing Tests

Tests are organized in the `tests/` directory. Test files should:
- Be named `test_*.py`
- Use pytest fixtures from `tests/conftest.py`
- Mock external dependencies (Cloudinary, email, Discord, etc.)
- Test both success and error cases

Example test:
```python
import pytest
from unittest.mock import patch

@pytest.mark.django_db
def test_my_view(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    response = api_client.get('/api/endpoint/')
    assert response.status_code == 200
```

## Running Migrations

From the repository root:
```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

## Common Management Commands

All Django management commands should be run from the `src/` directory:

```bash
cd src

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Start Django shell
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick Start:**
1. Create a new branch for your feature
2. Write tests for new functionality
3. Ensure all tests pass: `poetry run pytest`
4. Follow the [Django Best Practices](DJANGO_BEST_PRACTICES.md)
5. Submit a pull request

**Key Guidelines:**
- Use explicit imports (no `from module import *`)
- Add `app_name` to all `urls.py` files
- Name all URL patterns
- Write tests for all new code
- Add docstrings to public functions

See [DJANGO_BEST_PRACTICES.md](DJANGO_BEST_PRACTICES.md) for comprehensive coding standards.

## CI/CD

The project uses GitHub Actions for continuous integration:
- Tests run on Python 3.11 and 3.12
- Coverage reports are generated and uploaded to Codecov
- Linting can be added as needed

The CI workflow is defined in `.github/workflows/ci.yml`

## Deployment

### Environment Variables for Production

Set these environment variables in your production environment:

```bash
DJANGO_SETTINGS_MODULE=parts_webapi.settings.production
SECRET_KEY=<your-secure-secret-key>
DEBUG=False
ENVIRONMENT=main  # or 'uat' for staging
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
DB_PORT=5432
```

### WSGI/ASGI

For production deployment with Gunicorn:
```bash
cd src
gunicorn parts_webapi.wsgi:application --bind 0.0.0.0:8000
```

For ASGI (async) with Uvicorn:
```bash
cd src
uvicorn parts_webapi.asgi:application --host 0.0.0.0 --port 8000
```

## License

[Add your license information here]

## Contact

Team 3492 - team3492@gmail.com

## Manual Testing Steps for Reviewers

After pulling this branch, follow these steps to test the new structure:

1. **Install dependencies**:
   ```bash
   poetry install --with dev
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your SECRET_KEY and other settings
   ```

3. **Run migrations**:
   ```bash
   cd src
   python manage.py migrate
   ```

4. **Run tests**:
   ```bash
   cd .. # back to root
   poetry run pytest
   ```

5. **Start dev server**:
   ```bash
   cd src
   python manage.py runserver
   ```

6. **Verify the API** is accessible at http://127.0.0.1:8000/

All existing functionality should work exactly as before, just with a better organized project structure.
