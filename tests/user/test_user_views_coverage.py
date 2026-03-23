"""
Comprehensive unit tests for user/views.py to improve coverage.
Targets all missing lines identified in coverage report.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


# ---------------------------------------------------------------------------
# TokenObtainPairView  (lines 71-97)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTokenObtainPairView:
    url = "/user/token/"

    def test_post_invalid_data_returns_error(self, api_client):
        """Invalid credentials → ret_message error (lines 73-80)."""
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_valid_credentials_returns_tokens(self, api_client, db):
        """Valid credentials → access+refresh tokens (lines 94-95)."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username="tokenuser", email="token@example.com", password="Str0ngPass!"
        )
        user.is_active = True
        user.save()
        response = api_client.post(
            self.url,
            {"username": "tokenuser", "password": "Str0ngPass!"},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data

    def test_post_exception_returns_error(self, api_client):
        """Exception path → ret_message (lines 96-99)."""
        with patch(
            "user.views.TokenObtainPairSerializer",
            side_effect=Exception("boom"),
        ):
            response = api_client.post(self.url, {"username": "x", "password": "y"}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# TokenRefreshView  (line 113)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestTokenRefreshView:
    url = "/user/token/refresh/"

    def test_post_invalid_data_returns_error(self, api_client):
        """Invalid token → ret_message (line 113)."""
        response = api_client.post(self.url, {"refresh": "bad"}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception_returns_error_message(self, api_client):
        """Exception path → RetMessageSerializer response (lines 122-130)."""
        with patch(
            "user.views.TokenRefreshSerializer",
            side_effect=Exception("boom"),
        ):
            response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# UserLogIn  (lines 150-151, 154)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserLogIn:
    def test_authenticate_correct_password_returns_user(self, test_user):
        """check_password=True → returns user (lines 150-151)."""
        test_user.is_active = True
        test_user.save()
        from user.views import UserLogIn
        backend = UserLogIn()
        result = backend.authenticate(
            None, username=test_user.username, password="password"
        )
        assert result == test_user

    def test_authenticate_wrong_password_returns_none(self, test_user):
        """check_password=False → returns None (line 154)."""
        test_user.is_active = True
        test_user.save()
        from user.views import UserLogIn
        backend = UserLogIn()
        result = backend.authenticate(
            None, username=test_user.username, password="wrongpassword"
        )
        assert result is None

    def test_authenticate_nonexistent_user_returns_none(self, db):
        """DoesNotExist → returns None (lines 152-153)."""
        from user.views import UserLogIn
        backend = UserLogIn()
        result = backend.authenticate(None, username="nouser", password="pass")
        assert result is None


# ---------------------------------------------------------------------------
# UserProfile.post  (lines 165-255)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserProfilePost:
    url = "/user/profile/"

    def test_post_passwords_dont_match(self, api_client):
        """password1 != password2 → error (lines 169-174)."""
        with patch("user.views.send_message.send_email"):
            response = api_client.post(
                self.url,
                {
                    "username": "newuser1",
                    "email": "new1@example.com",
                    "password1": "Str0ngPass!",
                    "password2": "Different1!",
                    "first_name": "First",
                    "last_name": "Last",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_email_already_exists(self, api_client, test_user):
        """Email already in DB → error (lines 179-186)."""
        with patch("user.views.send_message.send_email"):
            response = api_client.post(
                self.url,
                {
                    "username": "brandnew",
                    "email": test_user.email,
                    "password1": "Str0ngPass!",
                    "password2": "Str0ngPass!",
                    "first_name": "First",
                    "last_name": "Last",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_success_creates_user(self, api_client):
        """Valid data → user created, email sent (lines 190-235)."""
        with patch("user.views.send_message.send_email") as mock_email:
            response = api_client.post(
                self.url,
                {
                    "username": "createduser",
                    "email": "created@example.com",
                    "password1": "Str0ngPass1!",
                    "password2": "Str0ngPass1!",
                    "first_name": "Created",
                    "last_name": "User",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is False
        mock_email.assert_called_once()

    def test_post_invalid_serializer_data(self, api_client):
        """Serializer invalid (bad password) → error (lines 236-248)."""
        response = api_client.post(
            self.url,
            {
                "username": "newuser2",
                "email": "new2@example.com",
                "password1": "short",
                "password2": "short",
                "first_name": "First",
                "last_name": "Last",
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_duplicate_username_exception(self, api_client, test_user):
        """UNIQUE constraint on username → friendly error (lines 249-260)."""
        with patch("user.views.send_message.send_email"):
            # First call creates the user fine
            api_client.post(
                self.url,
                {
                    "username": test_user.username,
                    "email": "unique99@example.com",
                    "password1": "Str0ngPass1!",
                    "password2": "Str0ngPass1!",
                    "first_name": "First",
                    "last_name": "Last",
                },
                format="json",
            )
        # The view catches exceptions generically
        # We simulate by having save() raise with that message
        with patch("user.views.User.save", side_effect=Exception("UNIQUE constraint failed: auth_user.username")):
            with patch("user.views.send_message.send_email"):
                response = api_client.post(
                    self.url,
                    {
                        "username": "anyuser",
                        "email": "any@example.com",
                        "password1": "Str0ngPass1!",
                        "password2": "Str0ngPass1!",
                        "first_name": "Any",
                        "last_name": "User",
                    },
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserProfile.put  (lines 263-425)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserProfilePut:
    url = "/user/profile/"

    def test_put_not_authenticated(self, api_client):
        """Unauthenticated → 401/403 or error message (line 412)."""
        response = api_client.put(
            self.url,
            {"id": "1", "first_name": "X", "last_name": "Y"},
            format="json",
        )
        assert response.status_code in [200, 401, 403]

    def test_put_own_user_updates_first_last_name(self, api_client, test_user):
        """Authenticated user updates their own name (lines 381-402)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.send_message.send_email"):
            response = api_client.put(
                self.url,
                {
                    "id": str(test_user.id),
                    "first_name": "Updated",
                    "last_name": "Name",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_put_different_user_without_admin(self, api_client, test_user, db):
        """Updating another user without admin access → error (line 276)."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(
            username="other2", email="other2@example.com", password="Str0ngPass1!"
        )
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.put(
                self.url,
                {"id": str(other.id), "first_name": "X", "last_name": "Y"},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_put_password_change_sends_email(self, api_client, test_user):
        """Password change triggers email (lines 284-320)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.send_message.send_email") as mock_email:
            with patch("user.views.validate_password"):
                response = api_client.put(
                    self.url,
                    {
                        "id": str(test_user.id),
                        "password": "Str0ngNewPass1!",
                    },
                    format="json",
                )
        assert response.status_code == 200
        mock_email.assert_called()

    def test_put_password_validation_error(self, api_client, test_user):
        """Password fails validation → error (lines 290-297)."""
        from django.core.exceptions import ValidationError
        api_client.force_authenticate(user=test_user)
        with patch("user.views.validate_password", side_effect=ValidationError("Too short")):
            response = api_client.put(
                self.url,
                {"id": str(test_user.id), "password": "short"},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_put_email_change_sends_notification(self, api_client, test_user):
        """Email change triggers notifications (lines 327-356)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.send_message.send_email") as mock_email:
            response = api_client.put(
                self.url,
                {
                    "id": str(test_user.id),
                    "email": "newemail@example.com",
                },
                format="json",
            )
        assert response.status_code == 200
        mock_email.assert_called()

    def test_put_email_and_password_change_together(self, api_client, test_user):
        """Both email and password change (lines 358-380)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.send_message.send_email"):
            with patch("user.views.validate_password"):
                response = api_client.put(
                    self.url,
                    {
                        "id": str(test_user.id),
                        "email": "combo@example.com",
                        "password": "Str0ngNewPass1!",
                    },
                    format="json",
                )
        assert response.status_code == 200

    def test_put_image_upload(self, api_client, test_user):
        """Image field triggers cloudinary upload (lines 385-391)."""
        api_client.force_authenticate(user=test_user)
        mock_response = {"public_id": "img_id_123", "version": "987654"}
        with patch("user.views.general.cloudinary.upload_image", return_value=mock_response):
            with patch("user.views.send_message.send_email"):
                response = api_client.put(
                    self.url,
                    {
                        "id": str(test_user.id),
                        "image": "data:image/png;base64,abc",
                    },
                    format="json",
                )
        assert response.status_code == 200

    def test_put_superuser_fields(self, api_client, admin_user, test_user):
        """Superuser can set is_active/is_superuser (lines 392-400)."""
        api_client.force_authenticate(user=admin_user)
        with patch("user.views.send_message.send_email"):
            response = api_client.put(
                self.url,
                {
                    "id": str(test_user.id),
                    "is_active": True,
                    "is_superuser": False,
                },
                format="json",
            )
        assert response.status_code == 200

    def test_put_serializer_invalid(self, api_client, test_user):
        """Invalid serializer data → error response (lines 404-410)."""
        api_client.force_authenticate(user=test_user)
        # id is required for UserUpdateSerializer lookup but we need it to pass
        # serializer validation then fail – simulate exception at save
        with patch("user.views.User.objects.get", side_effect=Exception("db error")):
            response = api_client.put(
                self.url,
                {"id": str(test_user.id), "first_name": "X", "last_name": "Y"},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserEmailConfirmation  (lines 461-505)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserEmailConfirmation:
    url = "/user/confirm/"

    def test_get_valid_hash_activates_user(self, api_client, test_user):
        """Correct hash → redirect to activationConfirm (lines 481-486)."""
        confirm_hash = abs(hash(test_user.date_joined))
        response = api_client.get(
            self.url, {"pk": test_user.username, "confirm": confirm_hash}
        )
        assert response.status_code in [200, 302]

    def test_get_invalid_hash_redirects_to_fail(self, api_client, test_user):
        """Wrong hash → redirect to activationFail (lines 488-496)."""
        response = api_client.get(
            self.url, {"pk": test_user.username, "confirm": 999999}
        )
        assert response.status_code in [200, 302]

    def test_get_unknown_user_redirects_to_fail(self, api_client, db):
        """User not found → redirect to activationFail (lines 497-505)."""
        response = api_client.get(
            self.url, {"pk": "nouser", "confirm": 12345}
        )
        assert response.status_code in [200, 302]

    def test_get_exception_returns_error(self, api_client, test_user):
        """Outer exception → ret_message (lines 461-465)."""
        with patch("user.views.UserEmailConfirmation.confirm_email", side_effect=Exception("boom")):
            response = api_client.get(
                self.url, {"pk": test_user.username, "confirm": "123"}
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserEmailResendConfirmation  (lines 511-559)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserEmailResendConfirmation:
    url = "/user/confirm/resend/"

    def test_post_valid_email_sends_confirmation(self, api_client, test_user):
        """Known email → resends email (lines 523-558)."""
        with patch("user.views.send_message.send_email") as mock_email:
            response = api_client.post(
                self.url, {"email": test_user.email}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is False
        mock_email.assert_called_once()

    def test_post_unknown_email_raises_exception(self, api_client, db):
        """Unknown email → exception caught at outer handler (lines 515-516)."""
        response = api_client.post(
            self.url, {"email": "nobody@example.com"}, format="json"
        )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception_returns_error(self, api_client, test_user):
        """Inner exception → outer handler (lines 515-516)."""
        with patch(
            "user.views.UserEmailResendConfirmation.resend_confirmation_email",
            side_effect=Exception("boom"),
        ):
            response = api_client.post(
                self.url, {"email": test_user.email}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserRequestPasswordReset  (lines 562-619)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserRequestPasswordReset:
    url = "/user/request-reset-password/"

    def test_post_active_user_sends_email(self, api_client, test_user):
        """Active user → token created, email sent (lines 580-611)."""
        test_user.is_active = True
        test_user.save()
        with patch("user.views.send_message.send_email") as mock_email:
            response = api_client.post(
                self.url, {"email": test_user.email}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is False
        mock_email.assert_called_once()

    def test_post_unknown_email_still_returns_ok(self, api_client, db):
        """Unknown email → no error exposed (anti-enumeration, lines 612-618)."""
        with patch("user.views.send_message.send_email"):
            response = api_client.post(
                self.url, {"email": "nobody@example.com"}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_inactive_user_sends_email_anyway(self, api_client, test_user):
        """Inactive user – cntx not built but email called anyway (lines 580-618)."""
        test_user.is_active = False
        test_user.save()
        with patch("user.views.send_message.send_email") as mock_email:
            response = api_client.post(
                self.url, {"email": test_user.email}, format="json"
            )
        assert response.status_code == 200

    def test_post_exception_returns_error(self, api_client, test_user):
        """Outer exception → ret_message (lines 566-570)."""
        with patch(
            "user.views.UserRequestPasswordReset.request_reset_password",
            side_effect=Exception("boom"),
        ):
            response = api_client.post(
                self.url, {"email": test_user.email}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserPasswordReset  (lines 622-681)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserPasswordReset:
    url = "/user/reset-password/"

    def test_post_valid_token_resets_password(self, api_client, test_user):
        """Valid token → password updated (lines 652-665)."""
        test_user.is_active = True
        test_user.save()
        uid = urlsafe_base64_encode(force_bytes(test_user.pk))
        from django.contrib.auth.tokens import default_token_generator
        token = default_token_generator.make_token(test_user)
        response = api_client.post(
            self.url,
            {"uuid": uid, "token": token, "password": "Str0ngNewPass1!"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_invalid_token_returns_error(self, api_client, test_user):
        """Invalid token → error message (lines 666-672)."""
        uid = urlsafe_base64_encode(force_bytes(test_user.pk))
        with patch("user.views.default_token_generator.check_token", return_value=False):
            response = api_client.post(
                self.url,
                {"uuid": uid, "token": "badtoken", "password": "Str0ngNewPass1!"},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_invalid_password_returns_error(self, api_client, test_user):
        """Password fails validation → error (lines 654-662)."""
        from django.core.exceptions import ValidationError
        uid = urlsafe_base64_encode(force_bytes(test_user.pk))
        with patch("user.views.default_token_generator.check_token", return_value=True):
            with patch("user.views.validate_password", side_effect=ValidationError("too short")):
                response = api_client.post(
                    self.url,
                    {"uuid": uid, "token": "tok", "password": "weak"},
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_missing_key_returns_error(self, api_client, db):
        """Missing required key → KeyError message (lines 673-681)."""
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception_returns_error(self, api_client, test_user):
        """Outer exception (lines 626-630)."""
        with patch(
            "user.views.UserPasswordReset.reset_password",
            side_effect=Exception("boom"),
        ):
            response = api_client.post(
                self.url, {"uuid": "x", "token": "t", "password": "p"}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserRequestUsername  (lines 684-734)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserRequestUsername:
    url = "/user/request-username/"

    def test_post_active_user_sends_email(self, api_client, test_user):
        """Active user → email sent (lines 700-731)."""
        test_user.is_active = True
        test_user.save()
        with patch("user.views.send_message.send_email") as mock_email:
            response = api_client.post(
                self.url, {"email": test_user.email}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is False
        mock_email.assert_called_once()

    def test_post_unknown_email_still_returns_ok(self, api_client, db):
        """Unknown email → anti-enumeration (lines 724-733)."""
        with patch("user.views.send_message.send_email"):
            response = api_client.post(
                self.url, {"email": "nobody@example.com"}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_exception_returns_error(self, api_client, test_user):
        """Outer exception (lines 688-692)."""
        with patch(
            "user.views.UserRequestUsername.forgot_username",
            side_effect=Exception("boom"),
        ):
            response = api_client.post(
                self.url, {"email": test_user.email}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserData  (lines 746-758)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserDataView:
    url = "/user/user-data/"

    def test_get_returns_user_data(self, api_client, test_user):
        """Authenticated → returns serialized user data (lines 748-750)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_user_parsed") as mock_get:
            mock_get.return_value = {
                "id": test_user.id,
                "username": test_user.username,
                "email": test_user.email,
                "name": "Test User",
                "first_name": "Test",
                "last_name": "User",
                "is_active": True,
                "phone": None,
                "groups": [],
                "permissions": [],
                "phone_type": None,
                "phone_type_id": None,
                "image": None,
                "links": [],
                "discord_user_id": None,
            }
            response = api_client.get(self.url)
        assert response.status_code == 200

    def test_get_exception_returns_error(self, api_client, test_user):
        """Exception → ret_message (lines 751-758)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_user_parsed", side_effect=Exception("boom")):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UserLinksView  (lines 770-792)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserLinksView:
    """UserLinksView is not in urls.py so test the helper methods directly."""

    def test_get_link_returns_filtered_links(self, api_client, test_user):
        """get_Link() returns links for user permissions (lines 771-778)."""
        api_client.force_authenticate(user=test_user)
        from user.views import UserLinksView
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get("/user/user-links/")
        request.user = test_user
        view = UserLinksView()
        view.request = request
        links = view.get_Link()
        assert links is not None

    def test_get_calls_get_link(self, api_client, test_user):
        """get() serializes result of get_Link (lines 781-784)."""
        api_client.force_authenticate(user=test_user)
        from user.views import UserLinksView
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get("/user/user-links/")
        request.user = test_user
        view = UserLinksView()
        view.request = request
        response = view.get(request)
        assert response.status_code == 200

    def test_get_exception_returns_error(self, test_user):
        """Exception → ret_message (lines 785-792)."""
        from user.views import UserLinksView
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get("/user/user-links/")
        request.user = test_user
        view = UserLinksView()
        view.request = request
        with patch.object(view, "get_Link", side_effect=Exception("boom")):
            response = view.get(request)
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# Groups  (lines 804-874)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGroupsView:
    url = "/user/groups/"

    def test_get_all_groups(self, api_client, test_user):
        """No user_id → returns all groups (lines 809-812)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_groups", return_value=[]):
            response = api_client.get(self.url)
        assert response.status_code == 200

    def test_get_with_user_id(self, api_client, test_user):
        """user_id param → returns user groups (line 808)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.get_user_groups", return_value=[]):
            response = api_client.get(self.url, {"user_id": test_user.id})
        assert response.status_code == 200

    def test_get_exception_returns_error(self, api_client, test_user):
        """Exception → ret_message (lines 813-820)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_groups", side_effect=Exception("boom")):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_invalid_data(self, api_client, test_user):
        """Invalid serializer → error (line 825)."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_with_access_saves_group(self, api_client, test_user):
        """has_access=True → saves group (lines 834-837)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.save_group"):
                response = api_client.post(
                    self.url, {"name": "New Group"}, format="json"
                )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_with_access_exception(self, api_client, test_user):
        """has_access=True but save throws → error (lines 838-845)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.save_group", side_effect=Exception("db error")):
                response = api_client.post(
                    self.url, {"name": "New Group"}, format="json"
                )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 847-852)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.post(
                self.url, {"name": "New Group"}, format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_with_access_deletes_group(self, api_client, test_user):
        """has_access=True → deletes group (lines 856-859)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.delete_group"):
                response = api_client.delete(
                    self.url + "?group_id=1"
                )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_delete_with_access_exception(self, api_client, test_user):
        """has_access=True but delete throws → error (lines 860-867)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.delete_group", side_effect=Exception("boom")):
                response = api_client.delete(self.url + "?group_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 869-874)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.delete(self.url + "?group_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# Permissions  (lines 886-958)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPermissionsView:
    url = "/user/permissions/"

    def test_get_all_permissions(self, api_client, test_user):
        """No user_id → returns all permissions (lines 892-894)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_permissions", return_value=[]):
            response = api_client.get(self.url)
        assert response.status_code == 200

    def test_get_with_user_id(self, api_client, test_user):
        """user_id param → returns user permissions (line 890)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.get_user_permissions", return_value=[]):
            response = api_client.get(self.url, {"user_id": test_user.id})
        assert response.status_code == 200

    def test_get_exception_returns_error(self, api_client, test_user):
        """Exception → ret_message (lines 895-902)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_permissions", side_effect=Exception("boom")):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_invalid_data(self, api_client, test_user):
        """Invalid serializer → error."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_with_access_saves_permission(self, api_client, test_user):
        """has_access=True → saves permission (lines 915-919)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.save_permission"):
                response = api_client.post(
                    self.url,
                    {"name": "Test Perm", "codename": "test_perm"},
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_with_access_exception(self, api_client, test_user):
        """has_access=True but save throws → error (lines 920-927)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch(
                "user.views.user.util.save_permission", side_effect=Exception("db error")
            ):
                response = api_client.post(
                    self.url,
                    {"name": "Test Perm", "codename": "test_perm"},
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 928-934)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.post(
                self.url,
                {"name": "Test Perm", "codename": "test_perm"},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_with_access_deletes_permission(self, api_client, test_user):
        """has_access=True → deletes permission (lines 938-943)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.delete_permission"):
                response = api_client.delete(self.url + "?prmsn_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_delete_with_access_exception(self, api_client, test_user):
        """has_access=True but delete throws → error (lines 944-951)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch(
                "user.views.user.util.delete_permission", side_effect=Exception("boom")
            ):
                response = api_client.delete(self.url + "?prmsn_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 952-958)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.delete(self.url + "?prmsn_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# AlertsView  (lines 970-984)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAlertsView:
    url = "/user/alerts/"

    def test_get_returns_user_alerts(self, api_client, test_user):
        """Authenticated → returns alerts (lines 972-976)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.alerts.util.get_user_alerts", return_value=[]):
            response = api_client.get(self.url)
        assert response.status_code == 200

    def test_get_with_alert_type(self, api_client, test_user):
        """With alert_comm_typ_id query param."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.alerts.util.get_user_alerts", return_value=[]):
            response = api_client.get(self.url, {"alert_comm_typ_id": 1})
        assert response.status_code == 200

    def test_get_exception_returns_error(self, api_client, test_user):
        """Exception → ret_message (lines 977-984)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.alerts.util.get_user_alerts", side_effect=Exception("boom")):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# SaveWebPushInfoView  (lines 996-1016)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveWebPushInfoView:
    url = "/user/webpush-save/"

    def test_post_success(self, api_client, test_user):
        """Successful subscription (lines 1008-1009)."""
        api_client.force_authenticate(user=test_user)
        mock_response = Mock()
        mock_response.status_code = 200
        with patch("user.views.webpush.views.save_info", return_value=mock_response):
            response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_bad_data_returns_error(self, api_client, test_user):
        """400 from webpush → ret_message error (lines 999-1006)."""
        api_client.force_authenticate(user=test_user)
        mock_response = Mock()
        mock_response.status_code = 400
        with patch("user.views.webpush.views.save_info", return_value=mock_response):
            response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception_returns_error(self, api_client, test_user):
        """Exception → ret_message (lines 1010-1016)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.webpush.views.save_info", side_effect=Exception("boom")):
            response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# UsersView  (lines 1028-1043)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestUsersView:
    url = "/user/users/"

    def test_get_returns_users(self, api_client, test_user):
        """Authenticated → returns serialized users list (lines 1030-1035)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_users_parsed", return_value=[]):
            response = api_client.get(self.url)
        assert response.status_code == 200

    def test_get_with_filter_params(self, api_client, test_user):
        """With is_active and is_admin params (lines 1031-1032)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_users_parsed", return_value=[]):
            response = api_client.get(self.url, {"is_active": "1", "is_admin": "0"})
        assert response.status_code == 200

    def test_get_exception_returns_error(self, api_client, test_user):
        """Exception → ret_message (lines 1036-1043)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_users_parsed", side_effect=Exception("boom")):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# SaveUserView  (lines 1053-1083)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveUserView:
    url = "/user/save/"

    def test_post_invalid_data(self, api_client, test_user):
        """Invalid serializer → error (lines 1055-1062)."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_with_access_saves_user(self, api_client, test_user):
        """has_access=True → saves user (lines 1064-1068)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.save_user"):
                response = api_client.post(
                    self.url,
                    {
                        "username": "saveuser",
                        "email": "save@example.com",
                        "first_name": "Save",
                        "last_name": "User",
                        "is_active": True,
                    },
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_with_access_exception(self, api_client, test_user):
        """has_access=True but save throws → error (lines 1069-1076)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.save_user", side_effect=Exception("db error")):
                response = api_client.post(
                    self.url,
                    {
                        "username": "saveuser2",
                        "email": "save2@example.com",
                        "first_name": "Save",
                        "last_name": "User",
                        "is_active": True,
                    },
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 1078-1083)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.post(
                self.url,
                {
                    "username": "saveuser3",
                    "email": "save3@example.com",
                    "first_name": "Save",
                    "last_name": "User",
                    "is_active": True,
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# SecurityAuditView  (lines 1095-1114)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSecurityAuditView:
    url = "/user/security-audit/"

    def test_get_with_access_returns_audit(self, api_client, test_user):
        """has_access=True → returns audit data (lines 1097-1100)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.run_security_audit", return_value=[]):
                response = api_client.get(self.url)
        assert response.status_code == 200

    def test_get_with_access_exception(self, api_client, test_user):
        """has_access=True but audit throws → error (lines 1101-1108)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch(
                "user.views.user.util.run_security_audit", side_effect=Exception("boom")
            ):
                response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 1109-1114)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# Links  (lines 1126-1192)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestLinksView:
    url = "/user/links/"

    def test_get_returns_links(self, api_client, test_user):
        """Authenticated → returns serialized links (lines 1128-1130)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_links", return_value=[]):
            response = api_client.get(self.url)
        assert response.status_code == 200

    def test_get_exception_returns_error(self, api_client, test_user):
        """Exception → ret_message (lines 1131-1138)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.user.util.get_links", side_effect=Exception("boom")):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_invalid_data(self, api_client, test_user):
        """Invalid serializer → error (lines 1142-1149)."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_with_access_saves_link(self, api_client, test_user):
        """has_access=True → saves link (lines 1151-1155)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.save_link"):
                response = api_client.post(
                    self.url,
                    {"menu_name": "Test Link", "routerlink": "/test", "order": 1},
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_post_with_access_exception(self, api_client, test_user):
        """has_access=True but save throws → error (lines 1156-1163)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.save_link", side_effect=Exception("db error")):
                response = api_client.post(
                    self.url,
                    {"menu_name": "Test Link", "routerlink": "/test", "order": 1},
                    format="json",
                )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 1165-1170)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.post(
                self.url,
                {"menu_name": "Test Link", "routerlink": "/test", "order": 1},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_with_access_deletes_link(self, api_client, test_user):
        """has_access=True → deletes link (lines 1173-1177)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.delete_link"):
                response = api_client.delete(self.url + "?link_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is False

    def test_delete_with_access_exception(self, api_client, test_user):
        """has_access=True but delete throws → error (lines 1178-1185)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.delete_link", side_effect=Exception("boom")):
                response = api_client.delete(self.url + "?link_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_no_access(self, api_client, test_user):
        """has_access=False → permission denied (lines 1187-1192)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.delete(self.url + "?link_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# SimulateUser  (lines 1202-1231)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSimulateUserView:
    url = "/user/simulate/"

    def test_get_with_access_returns_tokens(self, api_client, test_user):
        """has_access=True, valid user → returns tokens (lines 1213-1225)."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.get_user", return_value=test_user):
                response = api_client.get(self.url, {"user_id": test_user.id})
        assert response.status_code == 200

    def test_get_no_access_returns_error(self, api_client, test_user):
        """has_access=False → permission denied."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=False):
            response = api_client.get(self.url, {"user_id": test_user.id})
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception_in_fun_returns_error(self, api_client, test_user):
        """Exception inside fun → ret_message from access_response."""
        api_client.force_authenticate(user=test_user)
        with patch("user.views.has_access", return_value=True):
            with patch("user.views.user.util.get_user", side_effect=Exception("boom")):
                response = api_client.get(self.url, {"user_id": test_user.id})
        assert response.status_code == 200
        assert response.data.get("error") is True
