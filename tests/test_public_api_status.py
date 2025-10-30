import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from public.views import APIStatus

@pytest.mark.django_db
def test_api_status_returns_ok(api_rf, test_user):
    rf = api_rf
    request = rf.get("/api-status/")
    force_authenticate(request, user=test_user)

    view = APIStatus.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_200_OK
    assert hasattr(response, "data")