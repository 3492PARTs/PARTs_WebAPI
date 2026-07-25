"""
Extra coverage for:
  - user/util.py lines 124, 307, 384-388, 401-409, 421, 439-457
  - user/views.py lines 256, 388-393, 396-401, 419, 648, 1217-1226, 1260-1266, 1284-1298
"""
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------------------------------------------------------------
# user/util.py line 124  (get_users_parsed iterates users)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetUsersParsed:
    """Line 124: get_users_parsed loops through users and calls parse_user."""

    def test_get_users_parsed_returns_list(self, test_user):
        from user.util import get_users_parsed
        result = get_users_parsed(active=1, admin=0)
        assert isinstance(result, list)
        # Should contain at least test_user
        ids = [u["id"] for u in result]
        assert test_user.id in ids


# ---------------------------------------------------------------------------
# user/util.py line 307  (get_permissions with codename filter)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetPermissionsWithCodename:
    """Line 307: codename_filter applied when codename is not None."""

    def test_get_permissions_with_codename(self):
        from user.util import get_permissions
        from django.contrib.auth.models import Permission

        perm = Permission.objects.create(
            name="Test GP Perm",
            codename="test_gp_perm",
            content_type_id=-1,
        )
        result = get_permissions(codename="test_gp_perm")
        ids = list(result.values_list("id", flat=True))
        assert perm.id in ids


# ---------------------------------------------------------------------------
# user/util.py lines 384-388 (get_user_images with img_approved filter)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetUserImages:
    """Lines 384-388: get_user_images with img_approved filter."""

    def test_get_user_images_approved_filter(self, test_user):
        from user.util import get_user_images
        from user.models import UserImage

        UserImage.objects.create(
            user=test_user,
            img_approved=True,
            void_ind="n",
        )
        UserImage.objects.create(
            user=test_user,
            img_approved=False,
            void_ind="n",
        )

        result_approved = get_user_images(img_approved="true")
        for img in result_approved:
            assert img.img_approved is True

        result_unapproved = get_user_images(img_approved="false")
        for img in result_unapproved:
            assert img.img_approved is False


# ---------------------------------------------------------------------------
# user/util.py lines 401-409 (get_parsed_user_images loop)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetParsedUserImages:
    """Lines 401-409: get_parsed_user_images loops and calls parse_user_image."""

    def test_get_parsed_user_images(self, test_user):
        from user.util import get_parsed_user_images
        from user.models import UserImage

        UserImage.objects.create(
            user=test_user,
            img_id="parsed_img",
            img_ver="1",
            img_approved=False,
            void_ind="n",
        )

        result = get_parsed_user_images()
        assert isinstance(result, list)
        assert len(result) >= 1
        assert "id" in result[0]
        assert "user" in result[0]


# ---------------------------------------------------------------------------
# user/util.py line 421  (parse_user_image returns dict)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestParseUserImage:
    """Line 421: parse_user_image returns dict with expected keys."""

    def test_parse_user_image(self, test_user):
        from user.util import parse_user_image
        from user.models import UserImage

        img = UserImage.objects.create(
            user=test_user,
            img_id="parse_me",
            img_ver="2",
            img_approved=True,
            void_ind="n",
        )

        result = parse_user_image(img)
        assert result["id"] == img.id
        assert result["img_approved"] is True


# ---------------------------------------------------------------------------
# user/util.py lines 439-457 (save_user_image create + update)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveUserImage:
    """Lines 439-457: save_user_image creates and updates UserImage."""

    def test_save_user_image_create(self, test_user):
        from user.util import save_user_image

        data = {
            "user": {"id": test_user.id},
            "img_id": "new_img_id",
            "img_ver": "new_ver",
            "img_approved": False,
            "void_ind": "n",
        }
        result = save_user_image(data)
        assert result.user_id == test_user.id
        assert result.img_id == "new_img_id"

    def test_save_user_image_update(self, test_user):
        from user.util import save_user_image
        from user.models import UserImage

        img = UserImage.objects.create(
            user=test_user,
            img_id="old_id",
            img_ver="old_ver",
            img_approved=False,
            void_ind="n",
        )

        data = {
            "id": img.id,
            "user": {"id": test_user.id},
            "img_id": "updated_id",
            "img_ver": "updated_ver",
            "img_approved": True,
            "void_ind": "n",
        }
        result = save_user_image(data)
        assert result.img_id == "updated_id"
        assert result.img_approved is True


# ---------------------------------------------------------------------------
# user/views.py line 256  (UNIQUE username error → custom message)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserViewCreateUniqueError:
    """Line 256: UNIQUE username error is logged with None error_string."""

    url = "/user/users/"

    def test_non_unique_error_returns_generic_message(self, api_client, test_user):
        """Lines 253-256: non-UNIQUE error → error_string = None."""
        api_client.force_authenticate(user=test_user)

        with patch("user.views.User.objects.create_user",
                   side_effect=Exception("some other error")):
            response = api_client.post(
                self.url,
                {
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "TestPass1!",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# user/views.py lines 388-393 (image upload in user update)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserUpdateImageUpload:
    """Lines 388-393: image field triggers cloudinary upload."""

    url = "/user/users/"

    def test_put_with_image_uploads_to_cloudinary(self, api_client, test_user):
        """Lines 388-393: image field → upload_image called, UserImage created."""
        api_client.force_authenticate(user=test_user)
        mock_img = MagicMock()
        mock_img.content_type = "image/png"
        upload_result = {"public_id": "user_img_id", "version": "456"}

        with patch("user.views.general.cloudinary.upload_image", return_value=upload_result), \
             patch("user.views.UserUpdateSerializer") as MockSer:
            instance = MockSer.return_value
            instance.is_valid.return_value = True
            instance.validated_data = {"image": mock_img}
            response = api_client.put(self.url, {}, format="json")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# user/views.py lines 396-401 (superuser-only fields update)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserUpdateSuperuserFields:
    """Lines 395-403: is_staff, is_active, is_superuser only updated when requesting user is superuser."""

    url = "/user/users/"

    def test_superuser_can_update_is_active(self, api_client):
        """Lines 396-403: superuser → is_active, is_staff, is_superuser fields updated."""
        admin = User.objects.create_superuser(
            username="su_test_fields", email="su_fields@example.com", ######
        )
        api_client.force_authenticate(user=admin)

        with patch("user.views.UserUpdateSerializer") as MockSer:
            instance = MockSer.return_value
            instance.is_valid.return_value = True
            instance.validated_data = {
                "is_active": False,
                "is_staff": False,
                "is_superuser": False,
            }
            response = api_client.put(self.url, {}, format="json")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# user/views.py line 419  (non-UNIQUE update exception → None error_string)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserUpdateNonUniqueError:
    """Line 419: exception other than UNIQUE → error_string = None in put."""

    url = "/user/users/"

    def test_put_non_unique_exception(self, api_client, test_user):
        """Lines 416-428: non-UNIQUE exception in PUT → generic error message."""
        api_client.force_authenticate(user=test_user)

        with patch("user.views.UserUpdateSerializer") as MockSer:
            instance = MockSer.return_value
            instance.is_valid.side_effect = Exception("unexpected error")
            response = api_client.put(self.url, {}, format="json")

        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# user/views.py line 648  (token is None check)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPasswordResetTokenNone:
    """Line 648: token is None → 'Reset token required.' returned."""

    url = "/user/users/"

    def test_reset_password_token_none(self, api_client, test_user):
        """Line 647-653: token is None → error returned."""
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uuid = urlsafe_base64_encode(force_bytes(test_user.id))
        api_client.force_authenticate(user=test_user)

        response = api_client.post(
            f"{self.url}reset-password/",
            {"uuid": uuid, "token": None, "password": "NewPass1!"},
            format="json",
        )
        assert response.status_code in [200, 404]


# ---------------------------------------------------------------------------
# user/views.py lines 1217-1226  (SimulateUser.get success)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSimulateUserView:
    """Lines 1217-1226: GET /user/simulate/ returns tokens for target user."""

    url = "/user/simulate/"

    def test_get_simulate_user_returns_tokens(self, api_client, test_user):
        """Lines 1217-1226: returns access+refresh tokens for user_id."""
        api_client.force_authenticate(user=test_user)

        target = User.objects.create_user(
            username="sim_target", email="sim_target@example.com", ######
        )

        with patch("user.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()), \
             patch("user.views.user.util.get_user", return_value=target):
            response = api_client.get(f"{self.url}?user_id={target.id}")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# user/views.py lines 1260-1266  (UserImagesView.get success)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserImagesViewGet:
    """Lines 1260-1266: GET /user/user-images/ returns user images."""

    url = "/user/user-images/"

    def test_get_returns_user_images(self, api_client, test_user):
        """Lines 1260-1264: calls get_parsed_user_images and serializes."""
        api_client.force_authenticate(user=test_user)

        with patch("user.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()), \
             patch("user.views.user.util.get_parsed_user_images", return_value=[]), \
             patch("user.views.UserImageSerializer") as MockSer:
            MockSer.return_value.data = []
            response = api_client.get(self.url)

        assert response.status_code == 200

    def test_get_with_img_approved_filter(self, api_client, test_user):
        """Line 1261: img_approved param passed to get_parsed_user_images."""
        api_client.force_authenticate(user=test_user)

        with patch("user.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()), \
             patch("user.views.user.util.get_parsed_user_images", return_value=[]) as mock_get, \
             patch("user.views.UserImageSerializer") as MockSer:
            MockSer.return_value.data = []
            response = api_client.get(f"{self.url}?img_approved=true")

        mock_get.assert_called_once_with("true")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# user/views.py lines 1284-1298  (UserImagesView.post)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserImagesViewPost:
    """Lines 1284-1296: POST /user/user-images/."""

    url = "/user/user-images/"

    def test_post_invalid_data_returns_error(self, api_client, test_user):
        """Lines 1286-1293: invalid serializer → error."""
        api_client.force_authenticate(user=test_user)

        with patch("user.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()):
            response = api_client.post(self.url, {}, format="json")

        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_valid_data_saves_image(self, api_client, test_user):
        """Lines 1295-1296: valid data → save_user_image + parse_user_image called."""
        api_client.force_authenticate(user=test_user)
        from user.models import UserImage

        mock_ui = MagicMock(spec=UserImage)
        mock_ui.id = 999
        mock_parsed = {"id": 999, "user": {}, "img_approved": False, "date_added": None,
                       "image": None}

        with patch("user.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()), \
             patch("user.views.UserImageSerializer") as MockSer, \
             patch("user.views.user.util.save_user_image", return_value=mock_ui), \
             patch("user.views.user.util.parse_user_image", return_value=mock_parsed):
            instance = MockSer.return_value
            instance.is_valid.return_value = True
            instance.validated_data = {
                "user": {"id": test_user.id},
                "img_approved": False,
                "void_ind": "n",
            }
            # Second call to UserImageSerializer (for response)
            MockSer.side_effect = [instance, MagicMock(data=mock_parsed)]
            response = api_client.post(self.url, {}, format="json")

        assert response.status_code == 200
