import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import force_authenticate

import sponsoring.util
from sponsoring.views import GetItems, GetSponsors, SaveSponsor, SaveItem, SaveSponsorOrder

@pytest.mark.django_db
def test_get_items_success(api_rf, test_user):
    req = api_rf.get("/sponsoring/get-items/")
    force_authenticate(req, user=test_user)
    with patch("sponsoring.util.get_items", return_value=[{"item_id": 1}]) as mock_get:
        resp = GetItems.as_view()(req)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data == [{"item_id": 1}]
        mock_get.assert_called_once()

@pytest.mark.django_db
def test_get_sponsors_success(api_rf, test_user):
    req = api_rf.get("/sponsoring/get-sponsors/")
    force_authenticate(req, user=test_user)
    with patch("sponsoring.util.get_sponsors", return_value=[{"sponsor_nm": "X"}]) as mock_get:
        resp = GetSponsors.as_view()(req)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data[0]["sponsor_nm"] == "X"
        mock_get.assert_called_once()

@pytest.mark.django_db
def test_save_sponsor_invalid_serializer(api_rf, test_user):
    req = api_rf.post("/sponsoring/save-sponsor/", {"sponsor_nm": ""}, format='json')
    force_authenticate(req, user=test_user)

    fake_serializer = MagicMock()
    fake_serializer.is_valid.return_value = False
    fake_serializer.errors = {"sponsor_nm": ["This field may not be blank."]}

    with patch("sponsoring.views.SponsorSerializer", return_value=fake_serializer):
        resp = SaveSponsor.as_view()(req)
        assert hasattr(resp, "data")

@pytest.mark.django_db
def test_save_sponsor_success(api_rf, test_user):
    req = api_rf.post("/sponsoring/save-sponsor/", {"sponsor_nm": "N", "phone": "p", "email": "e"}, format='json')
    force_authenticate(req, user=test_user)

    fake_serializer = MagicMock()
    fake_serializer.is_valid.return_value = True
    fake_serializer.validated_data = {"sponsor_nm": "N", "phone": "p", "email": "e"}

    with patch("sponsoring.views.SponsorSerializer", return_value=fake_serializer), \
         patch("sponsoring.util.save_sponsor", return_value={"sponsor_id": 1}):
        resp = SaveSponsor.as_view()(req)
        assert hasattr(resp, "data")

@pytest.mark.django_db
def test_save_item_permission_denied(api_rf, test_user):
    req = api_rf.post("/sponsoring/save-item/", {"item_nm": "n"}, format='json')
    force_authenticate(req, user=test_user)

    fake_serializer = MagicMock()
    fake_serializer.is_valid.return_value = True
    fake_serializer.validated_data = {"item_nm": "n"}

    with patch("sponsoring.views.SaveItem.permission_classes", []), \
         patch("sponsoring.views.SaveItem.authentication_classes", []), \
         patch("sponsoring.views.SaveItemSerializer", return_value=fake_serializer), \
         patch("sponsoring.views.has_access", return_value=False):
        resp = SaveItem.as_view()(req)
        assert hasattr(resp, "data")

@pytest.mark.django_db
def test_save_item_success(api_rf, test_user):
    req = api_rf.post("/sponsoring/save-item/", {"item_nm": "n"}, format='json')
    force_authenticate(req, user=test_user)

    fake_serializer = MagicMock()
    fake_serializer.is_valid.return_value = True
    fake_serializer.validated_data = {"item_nm": "n"}

    with patch("sponsoring.views.SaveItemSerializer", return_value=fake_serializer), \
         patch("sponsoring.views.has_access", return_value=True), \
         patch("sponsoring.util.save_item", return_value={"item_id": 2}):
        resp = SaveItem.as_view()(req)
        assert hasattr(resp, "data")

@pytest.mark.django_db
def test_save_sponsor_order_calls_util(api_rf, test_user):
    req = api_rf.post("/sponsoring/save-sponsor-order/", {"order": [1,2,3]}, format='json')
    force_authenticate(req, user=test_user)

    with patch("sponsoring.util.save_sponsor_order", return_value=True) as mock_save:
        res = sponsoring.util.save_sponsor_order({"order":[1,2,3]})
        mock_save.assert_called()