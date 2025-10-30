import pytest
from rest_framework.test import APIClient, APIRequestFactory
from django.contrib.auth import get_user_model

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def api_rf():
    return APIRequestFactory()

@pytest.fixture
def test_user(db):
    User = get_user_model()
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
    return user
