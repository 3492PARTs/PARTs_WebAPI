"""
Extra coverage for scouting/admin/views.py:
  lines 357-364, 398-405, 458-469, 497-508, 534, 537, 568-569, 602, 635-636, 732-733, 749
"""
import pytest
from unittest.mock import patch, MagicMock

BASE = "/scouting/admin"


# ---------------------------------------------------------------------------
# lines 357-364  (RemoveTeamToEventView.post access denied)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestRemoveTeamToEventViewAccessDenied:
    """Lines 357-364: access denied path."""

    def test_post_access_denied(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/remove-team-to-event/",
                {"id": 1, "teams": []},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 363-370: exception path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.remove_link_team_to_event",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/remove-team-to-event/",
                {"id": 1, "teams": []},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# lines 398-405  (MatchView.post access denied)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestMatchViewAccessDenied:
    """Lines 398-405: MatchView.post access denied."""

    def test_post_access_denied(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/match/",
                {"match_key": "2099_qm1", "match_number": 1},
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# lines 458-469  (ScoutFieldScheduleView.post access denied + exception)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestScoutFieldScheduleAdminViewPost:
    """Lines 458-469: ScoutFieldScheduleView POST edge cases."""

    url = f"{BASE}/scout-field-schedule/"

    def test_post_access_denied(self, api_client, test_user):
        """Lines 462-467: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                self.url,
                {
                    "event_id": 1,
                    "st_time": "2099-01-01T09:00:00Z",
                    "end_time": "2099-01-01T10:00:00Z",
                    "void_ind": "n",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 468-475: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_scout_schedule",
                   side_effect=Exception("boom")):
            response = api_client.post(
                self.url,
                {
                    "event_id": 1,
                    "st_time": "2099-01-01T09:00:00Z",
                    "end_time": "2099-01-01T10:00:00Z",
                    "void_ind": "n",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# lines 497-508  (ScheduleView.post access denied + exception)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestScheduleViewPost:
    """Lines 497-508: ScheduleView POST edge cases."""

    url = f"{BASE}/schedule/"

    def test_post_access_denied(self, api_client, test_user):
        """Lines 501-506: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                self.url,
                {
                    "st_time": "2099-01-01T09:00:00Z",
                    "end_time": "2099-01-01T10:00:00Z",
                    "void_ind": "n",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 507-513: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_schedule",
                   side_effect=Exception("boom")):
            response = api_client.post(
                self.url,
                {
                    "st_time": "2099-01-01T09:00:00Z",
                    "end_time": "2099-01-01T10:00:00Z",
                    "void_ind": "n",
                },
                format="json",
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# lines 534, 537  (NotifyUserView.get - sch_id path and exception)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestNotifyUserViewGet:
    """Lines 534, 537: NotifyUserView GET sch_id path."""

    url = f"{BASE}/notify-user/"

    def test_get_sch_id_path(self, api_client, test_user):
        """Line 534: sch_id provided → notify_user called."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.notify_user",
                   return_value="notified"):
            response = api_client.get(f"{self.url}?sch_id=1")
        assert response.status_code == 200

    def test_get_no_id_raises_exception(self, api_client, test_user):
        """Line 536-537: no id → exception → error message."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True


# ---------------------------------------------------------------------------
# lines 568-569, 602  (ScoutingUserInfoView GET access denied + POST success)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestScoutingUserInfoView:
    """Lines 568-576, 602: ScoutingUserInfoView edge cases."""

    url = f"{BASE}/scouting-user-info/"

    def test_get_access_denied(self, api_client, test_user):
        """Lines 570-576: GET access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_success(self, api_client, test_user):
        """Line 602: POST success → 'Saved scout user info successfully.'"""
        from scouting.models import UserInfo

        api_client.force_authenticate(user=test_user)
        mock_ui = MagicMock(spec=UserInfo)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_scouting_user_info",
                   return_value=mock_ui), \
             patch("scouting.admin.views.ScoutingUserInfoSerializer") as MockSer:
            instance = MockSer.return_value
            instance.is_valid.return_value = True
            instance.validated_data = {
                "user": {"id": test_user.id},
                "group_leader": False,
                "under_review": False,
                "eliminate_results": False,
            }
            response = api_client.post(self.url, {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is not True


# ---------------------------------------------------------------------------
# lines 635-636  (MarkScoutPresentView.get success)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestMarkScoutPresentViewGet:
    """Lines 635-636: GET mark-scout-present/ success."""

    url = f"{BASE}/mark-scout-present/"

    def test_get_success(self, api_client, test_user):
        """Lines 631-636: success path."""
        api_client.force_authenticate(user=test_user)
        mock_sfs = MagicMock()

        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.util.get_scout_field_schedule",
                   return_value=mock_sfs), \
             patch("scouting.admin.views.scouting.field.util.check_in_scout",
                   return_value="checked in"):
            response = api_client.get(f"{self.url}?scout_field_sch_id=1&user_id={test_user.id}")
        assert response.status_code == 200
        assert "checked in" in str(response.data.get("retMessage", ""))


# ---------------------------------------------------------------------------
# lines 732-733  (FieldFormView.get success)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestFieldFormViewGet:
    """Lines 732-733: FieldFormView.get success."""

    url = f"{BASE}/field-form/"

    def test_get_returns_field_form(self, api_client, test_user):
        """Lines 731-733: success path."""
        api_client.force_authenticate(user=test_user)
        mock_ff = MagicMock()
        mock_ff.id = 1
        mock_ff.season_id = None
        mock_ff.img_url = None
        mock_ff.inv_img_url = None
        mock_ff.full_img_url = None

        with patch("scouting.admin.views.scouting.util.get_field_form", return_value=mock_ff), \
             patch("scouting.admin.views.FieldFormSerializer") as MockSer:
            MockSer.return_value.data = {"id": 1}
            response = api_client.get(self.url)
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# line 749  (FieldFormView.post access denied)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestFieldFormViewPostAccessDenied:
    """Line 749+: FieldFormView.post access denied."""

    url = f"{BASE}/field-form/"

    def test_post_access_denied(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(self.url, {"void_ind": "n"}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True
