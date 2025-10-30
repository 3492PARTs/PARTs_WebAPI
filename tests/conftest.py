import pytest
from rest_framework.test import APIClient, APIRequestFactory
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from unittest.mock import MagicMock, Mock

@pytest.fixture
def api_client():
    """Returns a DRF API client for making test requests."""
    return APIClient()

@pytest.fixture
def api_rf():
    """Returns a DRF API request factory."""
    return APIRequestFactory()

@pytest.fixture
def request_factory():
    """Returns a Django request factory."""
    return RequestFactory()

@pytest.fixture
def test_user(db):
    """Creates and returns a basic test user."""
    User = get_user_model()
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password"
    )
    return user

@pytest.fixture
def admin_user(db):
    """Creates and returns an admin test user."""
    User = get_user_model()
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass"
    )
    return user

@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """Returns an authenticated API client."""
    api_client.force_authenticate(user=test_user)
    return api_client

@pytest.fixture
def mock_cloudinary():
    """Returns a mock cloudinary module for testing."""
    mock = MagicMock()
    mock.uploader.upload.return_value = {
        "public_id": "test_image_id",
        "version": "1234567890"
    }
    mock.CloudinaryImage.return_value.build_url.return_value = "https://res.cloudinary.com/test/image/upload/v1234567890/test_image_id.jpg"
    return mock

@pytest.fixture
def mock_has_access():
    """Returns a mock for has_access function that returns True."""
    return Mock(return_value=True)

@pytest.fixture
def mock_has_access_false():
    """Returns a mock for has_access function that returns False."""
    return Mock(return_value=False)
