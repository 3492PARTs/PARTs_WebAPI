"""
Coverage tests for admin/views.py lines 259-262 (PhoneType update by ID).
"""
import pytest
from unittest.mock import patch


@pytest.mark.django_db
class TestPhoneTypeUpdateById:
    """Test updating an existing PhoneType by ID (lines 259-262)."""

    url = "/admin/phone-type/"

    def test_post_update_existing_phone_type(self, api_client, test_user):
        """Lines 259-262: update phone type when id is provided."""
        import user.models as user_models

        pt = user_models.PhoneType.objects.create(
            phone_type="Verizon", carrier="ATT"
        )

        test_user.is_superuser = True
        test_user.save()
        api_client.force_authenticate(user=test_user)

        with patch("admin.views.has_access", return_value=True):
            response = api_client.post(
                self.url,
                {"id": pt.id, "phone_type": "T-Mobile", "carrier": "T-Mobile"},
                format="json",
            )

        assert response.status_code == 200
        assert response.data.get("error") is not True

        pt.refresh_from_db()
        assert pt.phone_type == "T-Mobile"
        assert pt.carrier == "T-Mobile"

    def test_post_create_new_phone_type(self, api_client, test_user):
        """Lines 264-266: create phone type when id is absent."""
        test_user.is_superuser = True
        test_user.save()
        api_client.force_authenticate(user=test_user)

        with patch("admin.views.has_access", return_value=True):
            response = api_client.post(
                self.url,
                {"phone_type": "Sprint", "carrier": "Sprint"},
                format="json",
            )

        assert response.status_code == 200
        assert response.data.get("error") is not True
