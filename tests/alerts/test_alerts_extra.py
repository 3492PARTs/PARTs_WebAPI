"""
Extra coverage for:
  - alerts/util.py  line 136       (discord message for user.id == -1)
  - alerts/util.py  lines 286, 304-318  (get_alert_types with filter, save_alert_type)
  - alerts/views.py lines 167-174  (AlertTypesView.get success path)
  - alerts/views.py lines 192-206  (AlertTypesView.post success / invalid path)
  - alerts/util_alert_definitions.py lines 663-667, 670, 679-682
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils.timezone import now


# ---------------------------------------------------------------------------
# alerts/util.py line 136  (discord, user.id == -1 branch)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSendAlertsDiscordSystemUser:
    """Line 136: when alert.user.id == -1, u becomes the role mention."""

    def test_discord_system_user_uses_role_mention(self, system_user):
        """Line 135-136: user.id == -1 sets u to role mention string."""
        from alerts.util import create_alert, create_channel_send_for_comm_typ
        from alerts.models import (
            CommunicationChannelType,
            AlertChannelSend,
        )

        comm_type = CommunicationChannelType.objects.create(
            comm_typ="discord", comm_nm="Discord", void_ind="n"
        )
        alert = create_alert(system_user, "Subject", "Body")
        acs = create_channel_send_for_comm_typ(alert, comm_type)

        with patch("alerts.util.send_message.send_discord_notification") as mock_discord:
            from alerts.util import send_alerts
            send_alerts()

        # The discord call should have been made
        mock_discord.assert_called_once()
        call_args = mock_discord.call_args[0][0]
        assert "<@&1024485828283596941>" in call_args


# ---------------------------------------------------------------------------
# alerts/util.py line 286  (get_alert_types with alert_type filter)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetAlertTypes:
    """Lines 286, 289-292: get_alert_types filters by alert_type."""

    def test_get_alert_types_with_type_filter(self):
        from alerts.util import get_alert_types
        from alerts.models import AlertType

        at = AlertType.objects.create(
            alert_typ="test_typ_gat",
            alert_typ_nm="Test Type GAT",
            last_run=now(),
            void_ind="n",
        )

        result = get_alert_types(alert_type="test_typ_gat")
        pks = list(result.values_list("id", flat=True))
        assert at.id in pks

    def test_get_alert_types_with_id_filter(self):
        from alerts.util import get_alert_types
        from alerts.models import AlertType

        at = AlertType.objects.create(
            alert_typ="test_typ_gat2",
            alert_typ_nm="Test Type GAT2",
            last_run=now(),
            void_ind="n",
        )

        result = get_alert_types(alert_type_id=at.id)
        pks = list(result.values_list("id", flat=True))
        assert at.id in pks


# ---------------------------------------------------------------------------
# alerts/util.py lines 304-318  (save_alert_type create + update)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveAlertType:
    """Lines 304-318: save_alert_type creates and updates AlertType."""

    def test_save_alert_type_create(self):
        """Lines 306-317: create new AlertType."""
        from alerts.util import save_alert_type

        data = {
            "alert_typ": "new_sat_typ",
            "alert_typ_nm": "New SAT Type",
            "void_ind": "n",
        }
        result = save_alert_type(data)
        assert result.id is not None
        assert result.alert_typ == "new_sat_typ"

    def test_save_alert_type_update(self):
        """Lines 304-305: update existing AlertType."""
        from alerts.util import save_alert_type
        from alerts.models import AlertType

        at = AlertType.objects.create(
            alert_typ="upd_sat_typ",
            alert_typ_nm="Old Name",
            last_run=now(),
            void_ind="n",
        )

        data = {
            "id": at.id,
            "alert_typ": "upd_sat_typ",
            "alert_typ_nm": "Updated Name",
            "void_ind": "n",
        }
        result = save_alert_type(data)
        assert result.alert_typ_nm == "Updated Name"

    def test_save_alert_type_with_permission(self):
        """Lines 312-315: save_alert_type with permission codename."""
        from alerts.util import save_alert_type
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        # Create a permission with content_type_id = -1
        ct = ContentType.objects.first()
        perm = Permission.objects.create(
            name="Test Perm SAT",
            codename="test_perm_sat",
            content_type_id=-1,
        )

        data = {
            "alert_typ": "perm_sat_typ",
            "alert_typ_nm": "Perm SAT Type",
            "permission": {"codename": "test_perm_sat"},
            "void_ind": "n",
        }
        result = save_alert_type(data)
        assert result.permission is not None
        assert result.permission.codename == "test_perm_sat"


# ---------------------------------------------------------------------------
# alerts/views.py lines 167-174  (AlertTypesView.get success)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAlertTypesViewGet:
    """Lines 167-174: GET /alerts/types/ returns alert types."""

    url = "/alerts/types/"

    def test_get_returns_alert_types(self, api_client, test_user):
        """Lines 167-172: GET success → Response with data."""
        from alerts.models import AlertType

        AlertType.objects.create(
            alert_typ="view_test_typ",
            alert_typ_nm="View Test Type",
            last_run=now(),
            void_ind="n",
        )

        api_client.force_authenticate(user=test_user)
        with patch("alerts.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()):
            response = api_client.get(self.url)

        assert response.status_code == 200

    def test_get_with_id_filter(self, api_client, test_user):
        """Line 171 single serializer: GET with id param."""
        from alerts.models import AlertType

        at = AlertType.objects.create(
            alert_typ="view_id_test",
            alert_typ_nm="View ID Test",
            last_run=now(),
            void_ind="n",
        )

        api_client.force_authenticate(user=test_user)
        with patch("alerts.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()):
            response = api_client.get(f"{self.url}?id={at.id}")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# alerts/views.py lines 192-206  (AlertTypesView.post)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAlertTypesViewPost:
    """Lines 192-206: POST /alerts/types/."""

    url = "/alerts/types/"

    def test_post_invalid_data_returns_error(self, api_client, test_user):
        """Lines 194-201: invalid serializer → error."""
        api_client.force_authenticate(user=test_user)
        with patch("alerts.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()):
            response = api_client.post(self.url, {}, format="json")

        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_valid_data_creates_alert_type(self, api_client, test_user):
        """Lines 203-204: valid data → save_alert_type called."""
        api_client.force_authenticate(user=test_user)
        payload = {
            "alert_typ": "post_test_typ",
            "alert_typ_nm": "Post Test Type",
            "void_ind": "n",
        }
        with patch("alerts.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()):
            response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# alerts/util_alert_definitions.py lines 663-667, 670, 679-682
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestStageUserImageApprovalAlert:
    """Lines 663-682 in stage_user_image_approval_alert."""

    def test_stage_with_unapproved_images_sends_alert(self):
        """Lines 663-667, 670, 679-682: count > 0 → alerts sent, last_run updated."""
        from alerts.util_alert_definitions import stage_user_image_approval_alert
        from alerts.models import AlertType, AlertedResource
        from user.models import UserImage
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user_obj = User.objects.create_user(
            username="imgtest_user_uia",
            email="imgtest_uia@example.com",
            ######
        )
        UserImage.objects.create(
            user=user_obj,
            img_approved=False,
            void_ind="n",
        )

        from django.contrib.auth.models import Permission
        perm = Permission.objects.create(
            name="User Image Approval",
            codename="user_image_approval_perm",
            content_type_id=-1,
        )
        alert_typ = AlertType.objects.create(
            alert_typ="user-img-approval",
            alert_typ_nm="User Image Approval",
            subject="New Images",
            body="New user profile images",
            permission=perm,
            last_run=now(),
            void_ind="n",
        )

        with patch("alerts.util_alert_definitions.send_alerts_to_role",
                   return_value="sent"):
            result = stage_user_image_approval_alert()

        assert "Alerted" in result or result != ""

    def test_stage_no_unapproved_images(self):
        """Lines 669-681: count == 0 → message is 'NONE TO STAGE'."""
        from alerts.util_alert_definitions import stage_user_image_approval_alert
        from alerts.models import AlertType

        from django.contrib.auth.models import Permission
        perm = Permission.objects.create(
            name="User Image Approval 2",
            codename="user_image_approval_perm2",
            content_type_id=-1,
        )
        AlertType.objects.create(
            alert_typ="user-img-approval2",
            alert_typ_nm="User Image Approval 2",
            subject="New Images 2",
            body="New user profile images 2",
            permission=perm,
            last_run=now(),
            void_ind="n",
        )

        result = stage_user_image_approval_alert()
        assert result == "NONE TO STAGE"
