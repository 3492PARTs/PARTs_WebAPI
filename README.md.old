# PARTs WebAPI

Putnam Area Robotics Team Web API - A Django REST Framework application for managing team operations.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)

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

3. Set up environment variables (create a `.env` file or set in your environment):
```bash
export SECRET_KEY="your-secret-key"
export DEBUG="True"
export FRONTEND_ADDRESS="http://localhost:3000"
export ENVIRONMENT="local"
```

4. Run migrations:
```bash
poetry run python manage.py migrate
```

5. Start the development server:
```bash
poetry run python manage.py runserver
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
poetry run pytest tests/test_general_security.py
```

Run tests with verbose output:
```bash
poetry run pytest -v
```

### Coverage Reports

View coverage in terminal:
```bash
poetry run pytest --cov=. --cov-report=term-missing
```

Generate HTML coverage report:
```bash
poetry run pytest --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

### Coverage Requirements

This project maintains 100% test coverage. All pull requests must maintain this standard:
- The CI pipeline will fail if coverage drops below 100%
- Add tests for any new code you write
- Update tests when modifying existing code

### Writing Tests

Tests are organized in the `tests/` directory and within each Django app. Test files should:
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

## Contributing

1. Create a new branch for your feature
2. Write tests for new functionality
3. Ensure all tests pass: `poetry run pytest`
4. Ensure coverage remains at 100%
5. Submit a pull request

## CI/CD

The project uses GitHub Actions for continuous integration:
- Tests run on Python 3.11 and 3.12
- Coverage must be 100% or the build fails
- Coverage reports are uploaded to Codecov

## Project Structure

```
PARTs_WebAPI/
├── admin/           # Admin functionality
├── alerts/          # Alert system
├── attendance/      # Attendance tracking
├── form/            # Form management
├── general/         # Shared utilities
├── public/          # Public API endpoints
├── scouting/        # Scouting system
├── sponsoring/      # Sponsorship management
├── tba/             # The Blue Alliance integration
├── user/            # User management
├── tests/           # Test suite
└── api/             # Django settings and configuration
```

## License

[Add your license information here]

## Contact

Team 3492 - team3492@gmail.com
