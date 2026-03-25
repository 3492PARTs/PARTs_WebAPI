"""
Extra coverage tests for scouting/views.py.
The existing tests used wrong URLs (e.g. /scouting/seasons/ instead of /scouting/season/).
This file uses the correct URLs to cover the missing lines.
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestScoutingViewsCorrectURLs:
    """Cover missing lines 42-61, 79-94, 112-129, 147-161, 194, 216-217, 227, 251-260, 343-368, 378."""

    # ----- SeasonView -----

    def test_season_view_access_denied(self, api_client, test_user):
        """Lines 61-66: has_access=False → ret_message access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/season/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_season_view_success(self, api_client, test_user):
        """Lines 42-51: has_access=True, normal response."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_all_seasons", return_value=[]), \
             patch("scouting.views.scouting.util.get_current_season", return_value=MagicMock()):
            response = api_client.get("/scouting/season/")
        assert response.status_code == 200

    def test_season_view_current_param_success(self, api_client, test_user):
        """Lines 44-45: current=True branch."""
        mock_season = MagicMock()
        mock_season.season = "2024"
        mock_season.current = "y"
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_current_season", return_value=mock_season):
            response = api_client.get("/scouting/season/?current=true")
        assert response.status_code == 200

    def test_season_view_exception(self, api_client, test_user):
        """Lines 53-59: exception → ret_message error."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_all_seasons", side_effect=Exception("boom")):
            response = api_client.get("/scouting/season/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    # ----- EventView -----

    def test_event_view_access_denied(self, api_client, test_user):
        """Lines 94-99: has_access=False."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/event/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_event_view_success(self, api_client, test_user):
        """Lines 79-84: has_access=True success."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_all_events", return_value=[]):
            response = api_client.get("/scouting/event/")
        assert response.status_code == 200

    def test_event_view_exception(self, api_client, test_user):
        """Lines 86-92: exception path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_all_events", side_effect=Exception("boom")):
            response = api_client.get("/scouting/event/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    # ----- TeamView -----

    def test_team_view_access_denied(self, api_client, test_user):
        """Lines 129-134: has_access=False."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/team/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_team_view_success(self, api_client, test_user):
        """Lines 112-119: has_access=True success."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_teams", return_value=[]):
            response = api_client.get("/scouting/team/")
        assert response.status_code == 200

    def test_team_view_exception(self, api_client, test_user):
        """Lines 121-127: exception path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_teams", side_effect=Exception("boom")):
            response = api_client.get("/scouting/team/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    # ----- MatchView -----

    def test_match_view_access_denied(self, api_client, test_user):
        """Lines 161-166: has_access=False."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/match/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_match_view_success(self, api_client, test_user):
        """Lines 147-151: has_access=True success."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_matches", return_value=[]), \
             patch("scouting.views.scouting.util.get_current_event", return_value=MagicMock()):
            response = api_client.get("/scouting/match/")
        assert response.status_code == 200

    def test_match_view_exception(self, api_client, test_user):
        """Lines 153-159: exception path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_current_event", side_effect=Exception("boom")):
            response = api_client.get("/scouting/match/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    # ----- ScheduleView -----

    def test_schedule_view_access_denied(self, api_client, test_user):
        """Line 194: has_access=False."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/schedule/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    # ----- ScoutFieldScheduleView -----

    def test_scout_field_schedule_view_exception(self, api_client, test_user):
        """Lines 216-217: exception path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_current_scout_field_schedule_parsed",
                   side_effect=Exception("boom")):
            response = api_client.get("/scouting/scout-field-schedule/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_scout_field_schedule_view_access_denied(self, api_client, test_user):
        """Line 227: has_access=False."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/scout-field-schedule/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    # ----- ScheduleTypeView -----

    def test_schedule_type_view_exception(self, api_client, test_user):
        """Lines 251-258: exception path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_schedule_types", side_effect=Exception("boom")):
            response = api_client.get("/scouting/schedule-type/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_schedule_type_view_access_denied(self, api_client, test_user):
        """Lines 259-265: has_access=False."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/schedule-type/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    # ----- AllScoutingInfoView -----

    def test_all_scouting_info_view_success(self, api_client, test_user):
        """Lines 343-368: full success path."""
        api_client.force_authenticate(user=test_user)
        mock_event = MagicMock()
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_current_event", return_value=mock_event), \
             patch("scouting.views.scouting.util.get_all_seasons", return_value=[]), \
             patch("scouting.views.scouting.util.get_all_events", return_value=[]), \
             patch("scouting.views.scouting.util.get_teams", return_value=[]), \
             patch("scouting.views.scouting.util.get_matches", return_value=[]), \
             patch("scouting.views.scouting.util.get_current_schedule_parsed", return_value=[]), \
             patch("scouting.views.scouting.util.get_current_scout_field_schedule_parsed", return_value=[]), \
             patch("scouting.views.scouting.util.get_schedule_types", return_value=[]), \
             patch("scouting.views.scouting.strategizing.util.get_team_notes", return_value=[]), \
             patch("scouting.views.scouting.strategizing.util.get_match_strategies", return_value=[]), \
             patch("scouting.views.scouting.field.util.get_field_form", return_value={}), \
             patch("scouting.views.scouting.strategizing.util.get_alliance_selections", return_value=[]):
            response = api_client.get("/scouting/all-scouting-info/")
        assert response.status_code == 200

    def test_all_scouting_info_view_access_denied(self, api_client, test_user):
        """Line 378: has_access=False."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=False):
            response = api_client.get("/scouting/all-scouting-info/")
        assert response.status_code == 200
        assert response.data.get("error") is True
