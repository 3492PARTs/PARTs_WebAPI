# Django & Django REST Framework Best Practices

This document outlines the best practices followed in this project and serves as a guide for contributors.

## Project Structure

### Source Layout
```
PARTs_WebAPI/
├── src/                    # Application source code
│   ├── parts_webapi/      # Django project settings
│   │   ├── settings/      # Split settings (base, dev, prod, test)
│   │   ├── urls.py        # Root URL configuration
│   │   ├── wsgi.py        # WSGI application
│   │   └── asgi.py        # ASGI application
│   ├── [app_name]/        # Django apps
│   │   ├── migrations/    # Database migrations
│   │   ├── __init__.py
│   │   ├── admin.py       # Django admin configuration
│   │   ├── apps.py        # App configuration
│   │   ├── models.py      # Data models
│   │   ├── serializers.py # DRF serializers
│   │   ├── urls.py        # App URL patterns
│   │   ├── views.py       # View logic
│   │   └── util.py        # Helper functions (if needed)
│   └── manage.py          # Django management script
├── tests/                  # Test suite (organized by app)
├── templates/              # Django templates
├── .env.example           # Environment variables template
├── pyproject.toml         # Poetry dependencies
└── pytest.ini             # Test configuration
```

## Code Organization Best Practices

### 1. URL Configuration

#### Always Use Explicit Imports
❌ **Bad:**
```python
from .views import *
```

✅ **Good:**
```python
from .views import (
    UserView,
    GroupView,
    PermissionView,
)
```

#### Always Define app_name for Namespacing
```python
# In app/urls.py
app_name = "user"

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),
]
```

This enables URL reversal:
```python
from django.urls import reverse
url = reverse('user:profile')
```

#### Always Name Your URL Patterns
❌ **Bad:**
```python
path('profile/', UserProfileView.as_view()),
```

✅ **Good:**
```python
path('profile/', UserProfileView.as_view(), name='profile'),
```

### 2. Settings Organization

#### Use Split Settings
- `base.py` - Common settings for all environments
- `development.py` - Development-specific (DEBUG=True, console email)
- `production.py` - Production-specific (DEBUG=False, security headers)
- `test.py` - Test-specific (in-memory DB, simplified auth)

#### Environment Variables
Always use environment variables for sensitive data:
```python
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-for-development-only")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
```

### 3. Views Organization

#### Use DRF Generic Views and ViewSets
For simple CRUD operations, prefer:
- `generics.ListCreateAPIView`
- `generics.RetrieveUpdateDestroyAPIView`
- `viewsets.ModelViewSet`

#### Keep Views Focused
Each view class should handle one type of resource or action. If a views.py file exceeds 300-400 lines, consider:
1. Splitting into multiple files in a `views/` directory
2. Moving utility functions to `utils.py`
3. Using DRF ViewSets to reduce boilerplate

#### Authentication and Permissions
```python
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserProfileView(APIView):
    """API endpoint for user profile management."""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        # Implementation
        pass
```

### 4. Serializers Best Practices

#### Use ModelSerializer When Possible
For models with straightforward serialization:
```python
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']
```

#### Use Custom Serializers for Complex Logic
When you need custom validation or complex nested data, use `serializers.Serializer`.

### 5. Models Organization

#### Keep Models Clean
- Business logic should be in models or separate service files
- Use model managers for custom querysets
- Use `@property` for computed fields when appropriate

#### Use Related Names
```python
class Team(models.Model):
    members = models.ManyToManyField(
        User,
        related_name='teams',  # user.teams.all()
    )
```

### 6. Testing Structure

#### Organize Tests by App
```
tests/
├── conftest.py           # Shared fixtures
├── user/
│   ├── test_views.py
│   ├── test_models.py
│   └── test_serializers.py
├── alerts/
│   └── test_alerts.py
└── ...
```

#### Use Fixtures
```python
@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.mark.django_db
def test_user_creation(test_user):
    assert test_user.username == 'testuser'
```

### 7. Security Best Practices

#### Never Commit Secrets
- Use `.env` files (add to `.gitignore`)
- Use environment variables
- Provide `.env.example` template

#### Use HTTPS in Production
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

#### Validate User Input
Always use serializer validation:
```python
class UserCreationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
```

### 8. API Response Patterns

#### Consistent Response Format
```python
# Success
{
    "retMessage": "Operation successful",
    "error": false,
    "data": {...}
}

# Error
{
    "retMessage": "An error occurred",
    "error": true,
    "errorMessage": "Detailed error message"
}
```

### 9. Documentation

#### Docstrings for All Views
```python
class UserProfileView(APIView):
    """
    API endpoint for user profile management.
    
    Allows authenticated users to retrieve and update their profile information.
    
    Methods:
        GET: Retrieve user profile
        PUT: Update user profile
    """
    
    def get(self, request):
        """Retrieve the authenticated user's profile."""
        pass
```

### 10. Performance Considerations

#### Use select_related and prefetch_related
```python
# Avoid N+1 queries
users = User.objects.select_related('phone_type').all()
teams = Team.objects.prefetch_related('members').all()
```

#### Database Indexes
Add indexes for frequently queried fields:
```python
class User(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True, db_index=True)
```

## Common Patterns in This Project

### Authentication
- JWT tokens via `djangorestframework-simplejwt`
- Custom user model in `user.models.User`
- Token obtain: `POST /user/token/`
- Token refresh: `POST /user/token/refresh/`

### Permissions
- Custom permission checks via `general.security.has_access()`
- DRF's `IsAuthenticated` permission class
- Admin-only endpoints check with `has_access(user_id, "admin")`

### Error Handling
- Centralized error response via `general.security.ret_message()`
- Try-except blocks in all view methods
- Consistent error message format

### File Organization
- Large apps (like `scouting`) use sub-modules
- Utility functions in `util.py` files
- Separate `serializers.py` for all serialization logic

## Tools and Commands

### Running Tests
```bash
# All tests
poetry run pytest

# Without coverage (faster)
poetry run pytest --no-cov

# Specific app
poetry run pytest tests/user/

# With verbose output
poetry run pytest -v
```

### Database Migrations
```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### Running Development Server
```bash
cd src
python manage.py runserver
```

### Code Quality
Consider adding:
- `black` for code formatting
- `flake8` or `pylint` for linting
- `mypy` for type checking
- `isort` for import sorting

## References

- [Django Official Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
