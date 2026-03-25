"""
Coverage tests for scouting admin views (src/scouting/admin/views.py).
Covers lines: 104, 120-121, 130-152, 167-176, 197, 209-216, 232-239, 258-280,
302, 314-321, 343, 357-364, 386, 398-405, 447-469, 486-508, 525-546, 565-578,
587-611, 630-646, 671-678, 703-712, 730-735, 749, 761-768, 787-799
"""
import pytest
from unittest.mock import patch, MagicMock

BASE = "/scouting/admin"


@pytest.mark.django_db
class TestScoutAdminSeasonView:
    """SeasonView: POST/PUT/DELETE missing paths."""

    def test_post_invalid_data(self, api_client, test_user):
        """Line 104: invalid serializer data."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True):
            response = api_client.post(f"{BASE}/season/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 114-119: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/season/",
                {"season": "2025", "current": "n", "game": "G"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 120-127: exception path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_season",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/season/",
                {"season": "2025", "current": "n", "game": "G"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_put_invalid_data(self, api_client, test_user):
        """Line 130-140: PUT invalid serializer."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True):
            response = api_client.put(f"{BASE}/season/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_put_access_denied(self, api_client, test_user):
        """Lines 144-150: PUT access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.put(
                f"{BASE}/season/",
                {"season": "2025", "current": "n", "game": "G"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_put_exception(self, api_client, test_user):
        """Lines 151-158: PUT exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_season",
                   side_effect=Exception("boom")):
            response = api_client.put(
                f"{BASE}/season/",
                {"season": "2025", "current": "n", "game": "G"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_exception(self, api_client, test_user):
        """Lines 167-174: DELETE exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.delete_season",
                   side_effect=Exception("boom")):
            response = api_client.delete(f"{BASE}/season/?season_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_access_denied(self, api_client, test_user):
        """Lines 175-181: DELETE access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.delete(f"{BASE}/season/?season_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminEventView:
    """EventView: POST/DELETE missing paths."""

    def test_post_invalid_data(self, api_client, test_user):
        """Line 197: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/event/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 209-214: POST access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/event/",
                {"event_nm": "Test", "event_cd": "test", "date_st": "2024-01-01",
                 "date_end": "2024-01-02", "season_id": 1},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 215-222: POST exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_event",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/event/",
                {"event_nm": "Test", "event_cd": "test", "date_st": "2024-01-01",
                 "date_end": "2024-01-02", "season_id": 1},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_access_denied(self, api_client, test_user):
        """Lines 232-237: DELETE access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.delete(f"{BASE}/event/?event_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_exception(self, api_client, test_user):
        """Lines 238-244: DELETE exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.delete_event",
                   side_effect=Exception("boom")):
            response = api_client.delete(f"{BASE}/event/?event_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminTeamView:
    """TeamView: POST missing paths."""

    def test_post_invalid_data(self, api_client, test_user):
        """Lines 260-267: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/team/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 272-278: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/team/",
                {"team_no": 3492, "team_nm": "Test Team"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 279-286: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True):
            # Use a serializer that passes but then save fails
            with patch("scouting.admin.views.TeamCreateSerializer.save",
                       side_effect=Exception("boom")):
                response = api_client.post(
                    f"{BASE}/team/",
                    {"team_no": 3492, "team_nm": "Test Team"},
                    format="json"
                )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminTeamToEventView:
    """TeamToEventView: POST missing paths."""

    def test_post_invalid_data(self, api_client, test_user):
        """Line 302: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/team-to-event/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 314-319: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/team-to-event/",
                {"event_id": 1, "teams": []},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 320-327: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.link_team_to_event",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/team-to-event/",
                {"event_id": 1, "teams": []},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminMatchView:
    """MatchView: POST missing paths."""

    def test_post_invalid_data(self, api_client, test_user):
        """Line 386: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/match/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 398-403: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/match/",
                {"match_key": "test_qm1", "match_number": 1, "event_id": 1,
                 "comp_level": "qm", "time": None},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 404-411: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_match",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/match/",
                {"match_key": "test_qm1", "match_number": 1, "event_id": 1,
                 "comp_level": "qm", "time": None},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminFieldScheduleView:
    """ScoutFieldScheduleView: POST missing paths."""

    def test_post_invalid_data(self, api_client, test_user):
        """Lines 447-456: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/scout-field-schedule/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 461-466: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/scout-field-schedule/",
                {"event_id": 1, "st_time": "2024-01-01T10:00:00Z",
                 "end_time": "2024-01-01T11:00:00Z"},
                format="json"
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
                f"{BASE}/scout-field-schedule/",
                {"event_id": 1, "st_time": "2024-01-01T10:00:00Z",
                 "end_time": "2024-01-01T11:00:00Z"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminScheduleView:
    """ScheduleView: POST missing paths."""

    def test_post_invalid_data(self, api_client, test_user):
        """Lines 486-495: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/schedule/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 500-506: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/schedule/",
                {"sch_typ": "gen", "event_id": 1, "user_id": 1,
                 "st_time": "2024-01-01T10:00:00Z", "end_time": "2024-01-01T11:00:00Z"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 507-514: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_schedule",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/schedule/",
                {"sch_typ": "gen", "event_id": 1, "user_id": 1,
                 "st_time": "2024-01-01T10:00:00Z", "end_time": "2024-01-01T11:00:00Z"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminNotifyUserView:
    """NotifyUserView: GET missing paths."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 538-544: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/notify-user/?scout_field_sch_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user):
        """Lines 545-552: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.notify_users",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/notify-user/?scout_field_sch_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminScoutingUserInfoView:
    """ScoutingUserInfoView: GET/POST missing paths."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 571-576: GET access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/scouting-user-info/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user):
        """Lines 577-584: GET exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.get_scouting_user_info",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/scouting-user-info/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 604-608: POST access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/scouting-user-info/",
                {"user_id": 1, "under_review": False, "group_leader": False},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 610-617: POST exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.save_scouting_user_info",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/scouting-user-info/",
                {"user_id": 1, "under_review": False, "group_leader": False},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminMarkScoutPresentView:
    """MarkScoutPresentView: GET missing paths."""

    def test_get_exception(self, api_client, test_user):
        """Lines 637-644: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.util.get_scout_field_schedule",
                   side_effect=Exception("boom")):
            response = api_client.get(
                f"{BASE}/mark-scout-present/?scout_field_sch_id=1&user_id=1"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_access_denied(self, api_client, test_user):
        """Lines 645-651: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.get(
                f"{BASE}/mark-scout-present/?scout_field_sch_id=1&user_id=1"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminFieldResponseView:
    """FieldResponseView: DELETE missing paths."""

    def test_delete_access_denied(self, api_client, test_user):
        """Lines 671-676: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.delete(f"{BASE}/delete-field-result/?scout_field_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_exception(self, api_client, test_user):
        """Lines 677-684: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.void_field_response",
                   side_effect=Exception("boom")):
            response = api_client.delete(f"{BASE}/delete-field-result/?scout_field_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminPitResponseView:
    """PitResponseView: DELETE missing paths."""

    def test_delete_access_denied(self, api_client, test_user):
        """Lines 711-717: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.delete(f"{BASE}/delete-pit-result/?scout_pit_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_delete_exception(self, api_client, test_user):
        """Lines 703-710: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.void_scout_pit_response",
                   side_effect=Exception("boom")):
            response = api_client.delete(f"{BASE}/delete-pit-result/?scout_pit_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminFieldFormView:
    """FieldFormView: GET/POST missing paths."""

    def test_get_exception(self, api_client, test_user, system_user):
        """Lines 730-741: GET exception path (user_id=-1)."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.scouting.util.get_field_form",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/field-form/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_invalid_data(self, api_client, test_user):
        """Line 749: invalid serializer data."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True):
            response = api_client.post(f"{BASE}/field-form/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 761-766: POST access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/field-form/",
                {"season_id": 1},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutAdminScoutingReportView:
    """ScoutingReportView: GET missing paths."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 791-797: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/scouting-report/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user):
        """Lines 798-805: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.admin.views.has_access", return_value=True), \
             patch("scouting.admin.views.scouting.admin.util.scouting_report",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/scouting-report/")
        assert response.status_code == 200
        assert response.data.get("error") is True
