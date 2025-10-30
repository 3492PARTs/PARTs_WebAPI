"""
Pytest configuration and shared fixtures for PARTs WebAPI tests.
"""
import os
import pytest
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from faker import Faker

# Set up test environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('FRONTEND_ADDRESS', 'http://localhost:3000')
os.environ.setdefault('ENVIRONMENT', 'test')

fake = Faker()


@pytest.fixture
def api_client():
    """Provide a DRF API client for testing."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Provide an authenticated API client with a test user."""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def test_user(db):
    """Create a test user."""
    from user.models import User
    user = User.objects.create_user(
        username='testuser',
        email='testuser@test.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user with admin permissions."""
    from user.models import User
    user = User.objects.create_user(
        username='adminuser',
        email='admin@test.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )
    # Create admin group and permission
    admin_permission = Permission.objects.filter(codename='admin').first()
    if not admin_permission:
        content_type = ContentType.objects.get_for_model(User)
        admin_permission = Permission.objects.create(
            codename='admin',
            name='Can access admin',
            content_type=content_type
        )
    
    admin_group, _ = Group.objects.get_or_create(name='admin')
    admin_group.permissions.add(admin_permission)
    user.groups.add(admin_group)
    return user


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """Provide an authenticated API client with an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def mock_cloudinary(monkeypatch):
    """Mock cloudinary upload to avoid external calls."""
    def mock_upload(*args, **kwargs):
        return {
            'secure_url': 'https://test.cloudinary.com/test.jpg',
            'public_id': 'test_public_id'
        }
    
    monkeypatch.setattr('cloudinary.uploader.upload', mock_upload)
    return mock_upload


@pytest.fixture
def mock_tba_api(monkeypatch):
    """Mock TBA (The Blue Alliance) API calls."""
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            def json(self):
                return {'data': 'mocked'}
        return MockResponse()
    
    monkeypatch.setattr('requests.get', mock_get)
    return mock_get


@pytest.fixture
def test_phone_type(db):
    """Create a test phone type."""
    from user.models import PhoneType
    return PhoneType.objects.create(
        carrier='Test Carrier',
        phone_type='mobile'
    )


@pytest.fixture
def test_season(db):
    """Create a test season."""
    from public.season.models import Season
    return Season.objects.create(
        season='2024',
        current='y'
    )


@pytest.fixture
def test_error_log(db, test_user):
    """Create a test error log entry."""
    from admin.models import ErrorLog
    from django.utils import timezone
    return ErrorLog.objects.create(
        user=test_user,
        path='/test/path',
        message='Test error message',
        exception='Test exception',
        traceback='Test traceback',
        error_message='Test error',
        time=timezone.now()
    )


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass


@pytest.fixture
def faker_instance():
    """Provide a Faker instance for generating test data."""
    return Faker()
