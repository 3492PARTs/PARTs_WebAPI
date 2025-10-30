"""
Pytest configuration and fixtures for PARTs WebAPI tests.
"""
import os
import sys
from pathlib import Path
import pytest
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from rest_framework.test import APIClient
from model_bakery import baker

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set up test environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-12345678901234567890")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("FRONTEND_ADDRESS", "http://localhost:4200")
os.environ.setdefault("DB_ENGINE", "django.db.backends.sqlite3")
os.environ.setdefault("DB_NAME", ":memory:")
os.environ.setdefault("DB_USER", "")
os.environ.setdefault("DB_PASSWORD", "")
os.environ.setdefault("DB_HOST", "")
os.environ.setdefault("DB_PORT", "")
os.environ.setdefault("EMAIL_FROM", "test@test.com")
os.environ.setdefault("EMAIL_HOST", "smtp.test.com")
os.environ.setdefault("EMAIL_HOST_USER", "test@test.com")
os.environ.setdefault("EMAIL_HOST_PASSWORD", "testpass")
os.environ.setdefault("EMAIL_PORT", "587")
os.environ.setdefault("CLOUDINARY_URL", "cloudinary://test:test@test")
os.environ.setdefault("TBA_KEY", "test-tba-key")
os.environ.setdefault("TBA_WEBHOOK_SECRET", "test-webhook-secret")
os.environ.setdefault("DISCORD_NOTIFICATION_WEBHOOK", "https://discord.com/api/webhooks/test")
os.environ.setdefault("VAPID_PUBLIC_KEY", "test-public-key")
os.environ.setdefault("VAPID_PRIVATE_KEY", "test-private-key")
os.environ.setdefault("VAPID_ADMIN_EMAIL", "test@test.com")


def pytest_configure(config):
    """Configure pytest with Django settings."""
    import django
    from django.conf import settings as django_settings
    
    # Create dummy JWT key files if they don't exist
    keys_dir = BASE_DIR / "keys"
    keys_dir.mkdir(exist_ok=True)
    
    jwt_key = keys_dir / "jwt-key"
    jwt_pub_key = keys_dir / "jwt-key.pub"
    
    if not jwt_key.exists():
        # Generate a dummy RSA private key for testing
        jwt_key.write_text("""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF1o2RNL4qXqC2bGFzB0sATyLvHQC
b0h7RW5qvBZCzxQy9EhBJPwI2vXpVKzFvI1XfvvLPgr5q2DlIuKMZEhHC6yxKLFv
hQG2P/ixzU3dH9JJVwHBKRWHCfLh2FGMZBNxqNDWOPjKm2ZH4+zq7YQlp5fQvRJu
j7b0bMY0JpyGM7kWbBZC8cWjXqhNvfZqSLkJPLvZ1c3GdBCyZE3YqvSp0ZKCLCXM
w8XDXY0JVlC7u8bLME0S6xz7RQy2h5Vx0H+vBYQbCZ3hNPLPrFCCWYJe8HZJB0Zy
4TqFqXCQdLPbOw5qDqH8g8oBEqO0+YQqSqWHGQIDAQABAoIBABYKMSI2pQzC2aMI
UaC2l8GbBt9H2v7z5D8PmwQ0g+Z9vBdP3FGKMCjLqRKJ0H2qQG5Y3sG8V0H3YrBq
LqOyg7EQx5vfPqJYvKXe0BxZqFxPdGNF0NqHQWBqCZKqLPJGbOqXZHF0qH3YqYWL
CfQgE0VKMYqLEQGYYHWMCQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQECgYEA8ZRPvHqNQGOvBQYHGvLh6Z9XqNQqOqZvqZpQqZpQqZpQqZpQqZpQ
qZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQ
qZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQ
qZpQqZpQqZpQqZpQqZpQqZpQqZpQqZkCgYEA3XqZpQqZpQqZpQqZpQqZpQqZpQqZ
pQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZ
pQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZ
pQqZpQqZpQqZpQqZpQqZpQqZpQqZpQqZpQkCgYEA0Z3VS5JJcds3xfn/ygWyF1o2
RNL4qXqC2bGFzB0sATyLvHQCb0h7RW5qvBZCzxQy9EhBJPwI2vXpVKzFvI1XfvvL
Pgr5q2DlIuKMZEhHC6yxKLFvhQG2P/ixzU3dH9JJVwHBKRWHCfLh2FGMZBNxqNDW
OPjKm2ZH4+zq7YQlp5fQvRJuj7b0bMY0JpyGM7kWbBZC8cWjXqhNvfZqSLkJPLvZ
1c3GdBCyZE3YqvSp0ZKCLCXMw8XDXY0JVlC7u8bLMECgYBqCZKqLPJGbOqXZHF0
qH3YqYWLCfQgE0VKMYqLEQGYYHWMCQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQkCgYBqCZKqLPJGbOqXZHF0qH3Y
qYWLCfQgE0VKMYqLEQGYYHWMCQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMY
HQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQMYHQ==
-----END RSA PRIVATE KEY-----
""")
    
    if not jwt_pub_key.exists():
        # Generate a dummy RSA public key for testing
        jwt_pub_key.write_text("""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0Z3VS5JJcds3xfn/ygWy
F1o2RNL4qXqC2bGFzB0sATyLvHQCb0h7RW5qvBZCzxQy9EhBJPwI2vXpVKzFvI1X
fvvLPgr5q2DlIuKMZEhHC6yxKLFvhQG2P/ixzU3dH9JJVwHBKRWHCfLh2FGMZBNx
qNDWOPjKm2ZH4+zq7YQlp5fQvRJuj7b0bMY0JpyGM7kWbBZC8cWjXqhNvfZqSLkJ
PLvZ1c3GdBCyZE3YqvSp0ZKCLCXMw8XDXY0JVlC7u8bLME0S6xz7RQy2h5Vx0H+v
BYQbCZ3hNPLPrFCCWYJe8HZJB0Zy4TqFqXCQdLPbOw5qDqH8g8oBEqO0+YQqSqWH
GQIDAQAB
-----END PUBLIC KEY-----
""")
    
    django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Set up the test database."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user."""
    from user.models import User
    return baker.make(
        User,
        username='testuser',
        email='test@test.com',
        first_name='Test',
        last_name='User',
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def superuser(db):
    """Create a test superuser."""
    from user.models import User
    user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, superuser):
    """Create an admin authenticated API client."""
    api_client.force_authenticate(user=superuser)
    return api_client


@pytest.fixture
def permission(db):
    """Create a test permission."""
    return baker.make(Permission, content_type_id=-1, codename='test_permission')


@pytest.fixture
def group(db, permission):
    """Create a test group with permissions."""
    group = baker.make(Group)
    group.permissions.add(permission)
    return group


@pytest.fixture
def phone_type(db):
    """Create a test phone type."""
    from user.models import PhoneType
    return baker.make(PhoneType, carrier='Test Carrier', phone_type='Mobile')


@pytest.fixture
def link(db, permission):
    """Create a test link."""
    from user.models import Link
    return baker.make(
        Link,
        permission=permission,
        menu_name='Test Link',
        routerlink='/test',
        order=1
    )


@pytest.fixture
def error_log(db, user):
    """Create a test error log."""
    from admin.models import ErrorLog
    from django.utils import timezone
    return baker.make(
        ErrorLog,
        user=user,
        path='/test/path',
        message='Test error',
        time=timezone.now()
    )


# Mock fixtures for external services
@pytest.fixture
def mock_cloudinary(mocker):
    """Mock Cloudinary upload."""
    return mocker.patch('general.cloudinary.upload_image', return_value={
        'public_id': 'test_id',
        'version': '123456'
    })


@pytest.fixture
def mock_send_email(mocker):
    """Mock email sending."""
    return mocker.patch('general.send_message.send_email', return_value=True)


@pytest.fixture
def mock_tba_api(mocker):
    """Mock TBA API calls."""
    return mocker.patch('requests.get', return_value=mocker.Mock(
        status_code=200,
        json=lambda: {'key': 'value'}
    ))


@pytest.fixture
def mock_discord_webhook(mocker):
    """Mock Discord webhook."""
    return mocker.patch('requests.post', return_value=mocker.Mock(status_code=200))
