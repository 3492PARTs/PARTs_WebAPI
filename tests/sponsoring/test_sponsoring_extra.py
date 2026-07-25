"""
Extra coverage for:
  - sponsoring/views.py line 80  (invalid data → ret_message)
  - user/models.py line 128      (UserImage.__str__)
"""
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# sponsoring/views.py line 80  (invalid data path)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSponsoringInvalidData:
    """Line 80: invalid serializer data returns error."""

    url = "/sponsoring/save-item/"

    def test_post_invalid_data_returns_error(self, api_client, test_user):
        """Line 80: SaveItemSerializer is invalid → ret_message with error."""
        api_client.force_authenticate(user=test_user)

        with patch("sponsoring.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()):
            response = api_client.post(self.url, {}, format="json")

        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# user/models.py line 128  (UserImage.__str__)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserImageStr:
    """Line 128: UserImage.__str__ returns '<id> <user>'."""

    def test_user_image_str(self, test_user):
        from user.models import UserImage

        img = UserImage.objects.create(
            user=test_user,
            img_id="test_img_id",
            img_ver="123",
            img_approved=False,
            void_ind="n",
        )
        s = str(img)
        assert str(img.id) in s
        assert str(test_user) in s
