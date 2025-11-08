# Contributing to PARTs WebAPI

Thank you for your interest in contributing to PARTs WebAPI! This document provides guidelines and best practices for contributing to this project.

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Poetry (for dependency management)
- Git

### Setup Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/3492PARTs/PARTs_WebAPI.git
   cd PARTs_WebAPI
   ```

2. **Install dependencies:**
   ```bash
   poetry install --with dev
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations:**
   ```bash
   cd src
   python manage.py migrate
   ```

5. **Run tests to ensure everything works:**
   ```bash
   cd ..  # Back to root
   poetry run pytest
   ```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-user-export` - for new features
- `bugfix/fix-login-issue` - for bug fixes
- `refactor/improve-views` - for refactoring
- `docs/update-readme` - for documentation

### 2. Make Your Changes

#### Code Style
- Follow PEP 8 style guide for Python code
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all public functions and classes

#### Best Practices
- See [DJANGO_BEST_PRACTICES.md](DJANGO_BEST_PRACTICES.md) for detailed guidelines
- Always use explicit imports (no `from module import *`)
- Add `app_name` to all `urls.py` files
- Name all URL patterns for easy reversal
- Write tests for new functionality
- Update documentation when changing behavior

### 3. Write Tests

All new features must include tests. We maintain high test coverage.

```python
# tests/your_app/test_your_feature.py
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_your_feature(api_client, test_user):
    """Test description of what this tests."""
    api_client.force_authenticate(user=test_user)
    response = api_client.get('/api/endpoint/')
    assert response.status_code == 200
```

### 4. Run Tests Locally

Before committing, ensure all tests pass:

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/user/test_views.py

# Run with coverage report
poetry run pytest --cov=src --cov-report=term-missing
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add user export functionality

- Add export view and serializer
- Add tests for export functionality
- Update documentation"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- First line: brief summary (50 chars or less)
- Blank line
- Detailed description (if needed)
- Reference issues: "Fixes #123" or "Related to #456"

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference to related issues
- Screenshots (if UI changes)

## Code Review Process

### What Reviewers Look For
- Code follows project conventions and best practices
- Tests are included and passing
- Documentation is updated
- No security vulnerabilities introduced
- Performance considerations addressed
- Code is maintainable and readable

### Responding to Feedback
- Be open to constructive criticism
- Address all review comments
- Ask questions if feedback is unclear
- Update PR based on feedback
- Re-request review when ready

## Project Structure Guidelines

### Adding a New App

1. **Create the app:**
   ```bash
   cd src
   python manage.py startapp app_name
   ```

2. **Follow the structure:**
   ```
   app_name/
   ├── __init__.py
   ├── admin.py           # Django admin configuration
   ├── apps.py            # App configuration
   ├── models.py          # Data models
   ├── serializers.py     # DRF serializers
   ├── urls.py            # URL patterns
   ├── views.py           # View logic
   ├── util.py            # Helper functions (optional)
   └── migrations/        # Database migrations
   ```

3. **Add to INSTALLED_APPS:**
   ```python
   # src/parts_webapi/settings/base.py
   INSTALLED_APPS = [
       # ...
       "app_name.apps.AppNameConfig",
   ]
   ```

4. **Create URL configuration:**
   ```python
   # src/app_name/urls.py
   from django.urls import path
   from .views import MyView
   
   app_name = "app_name"
   
   urlpatterns = [
       path('endpoint/', MyView.as_view(), name='endpoint'),
   ]
   ```

5. **Register URLs:**
   ```python
   # src/parts_webapi/urls.py
   urlpatterns = [
       # ...
       path("app_name/", include("app_name.urls")),
   ]
   ```

6. **Create tests directory:**
   ```bash
   mkdir tests/app_name
   touch tests/app_name/test_views.py
   ```

### Adding API Endpoints

When adding new API endpoints:

1. **Define the model** (if needed):
   ```python
   # app_name/models.py
   from django.db import models
   
   class MyModel(models.Model):
       name = models.CharField(max_length=255)
       created_at = models.DateTimeField(auto_now_add=True)
   ```

2. **Create serializer:**
   ```python
   # app_name/serializers.py
   from rest_framework import serializers
   from .models import MyModel
   
   class MyModelSerializer(serializers.ModelSerializer):
       class Meta:
           model = MyModel
           fields = ['id', 'name', 'created_at']
           read_only_fields = ['id', 'created_at']
   ```

3. **Create view:**
   ```python
   # app_name/views.py
   from rest_framework.views import APIView
   from rest_framework.response import Response
   from rest_framework.permissions import IsAuthenticated
   from rest_framework_simplejwt.authentication import JWTAuthentication
   
   class MyView(APIView):
       """API endpoint for managing MyModel objects."""
       authentication_classes = (JWTAuthentication,)
       permission_classes = (IsAuthenticated,)
       
       def get(self, request):
           """List all MyModel objects."""
           # Implementation
           pass
   ```

4. **Write tests:**
   ```python
   # tests/app_name/test_views.py
   import pytest
   
   @pytest.mark.django_db
   def test_myview_get(api_client, test_user):
       """Test MyView GET endpoint."""
       api_client.force_authenticate(user=test_user)
       response = api_client.get('/app_name/endpoint/')
       assert response.status_code == 200
   ```

## Testing Guidelines

### Types of Tests
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test multiple components together
- **API Tests**: Test API endpoints end-to-end

### Test Fixtures
Use fixtures from `tests/conftest.py`:
```python
@pytest.mark.django_db
def test_with_user(test_user, api_client):
    """test_user and api_client are fixtures."""
    api_client.force_authenticate(user=test_user)
    # Your test code
```

### Mocking External Services
Always mock external services (Cloudinary, email, Discord):
```python
def test_with_mock(mocker):
    mock_send = mocker.patch('general.send_message.send_email')
    # Your test code
    mock_send.assert_called_once()
```

## Security Guidelines

### Never Commit Secrets
- API keys
- Passwords
- Database credentials
- Secret keys

Use environment variables instead!

### Validate All User Input
- Use serializer validation
- Sanitize data before database operations
- Validate file uploads

### Check Permissions
Always check user permissions:
```python
from general.security import has_access

if not has_access(request.user.id, "admin"):
    return Response({"error": "Permission denied"}, status=403)
```

## Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Use type hints where appropriate
- Comment complex logic

### API Documentation
Update API documentation when:
- Adding new endpoints
- Changing endpoint behavior
- Modifying request/response format

### README Updates
Update README.md when:
- Changing setup process
- Adding new dependencies
- Modifying deployment process

## Getting Help

### Where to Ask Questions
- Create an issue on GitHub
- Contact team lead
- Check existing documentation

### Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Project Best Practices](DJANGO_BEST_PRACTICES.md)
- [Testing Guide](tests/README.md)

## License

By contributing to PARTs WebAPI, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Your contributions help make PARTs WebAPI better for everyone. Thank you for taking the time to contribute!
