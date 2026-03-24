"""
Coverage tests for scouting strategizing views (src/scouting/strategizing/views.py).
Covers missing lines: 70-85, 107, 119-120, 130, 145-154, 183-184, 202-215, 247-248,
302-315, 346-347
"""
import pytest
from unittest.mock import patch, MagicMock

BASE = "/scouting/strategizing"


@pytest.mark.django_db
class TestTeamNoteViewExtra:
    """TeamNoteView extra coverage."""

    def test_post_access_denied(self, api_client, test_user):
        """Lines 84-90: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/team-notes/",
                {"event_id": 1, "team_id": 1, "note": "test", "void_ind": "n"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_invalid_data(self, api_client, test_user):
        """Lines 61-68: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/team-notes/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 76-83: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.save_note",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/team-notes/",
                {"event_id": 1, "team_id": 1, "note": "test", "void_ind": "n"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestMatchStrategyViewExtra:
    """MatchStrategyView extra coverage."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 111-117: GET access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/match-strategy/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user, system_user):
        """Lines 119-125: GET exception (no user_id)."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.get_match_strategies",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/match-strategy/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_with_match_id(self, api_client, test_user):
        """Line 107: GET with match_id (single serializer) - patched at serializer level."""
        api_client.force_authenticate(user=test_user)
        mock_response = MagicMock()
        mock_response.data = {"id": 1, "strategy": "test"}
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.get_match_strategies",
                   return_value={}), \
             patch("scouting.strategizing.views.MatchStrategySerializer") as mock_ser:
            mock_ser.return_value.data = {"id": 1, "strategy": "test"}
            response = api_client.get(f"{BASE}/match-strategy/?match_id=1")
        assert response.status_code == 200

    def test_post_invalid_data(self, api_client, test_user):
        """Line 130: invalid serializer."""
        api_client.force_authenticate(user=test_user)
        response = api_client.post(f"{BASE}/match-strategy/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 153-159: POST access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/match-strategy/",
                {"match_id": 1, "strategy": "test", "void_ind": "n"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 145-152: POST exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.save_match_strategy",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/match-strategy/",
                {"match_id": 1, "strategy": "test", "void_ind": "n"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestAllianceSelectionViewExtra:
    """AllianceSelectionView extra coverage."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 175-181: GET access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/alliance-selection/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user, system_user):
        """Lines 183-189: GET exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.get_alliance_selections",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/alliance-selection/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 214-220: POST access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/alliance-selection/",
                [{"event_id": 1, "team_id": 1, "note": "", "order": 1, "void_ind": "n"}],
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 206-213: POST exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.save_alliance_selections",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/alliance-selection/",
                [{"event_id": 1, "team_id": 1, "note": "", "order": 1, "void_ind": "n"}],
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestGraphTeamViewExtra:
    """GraphTeamView extra coverage."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 239-245: GET access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/graph-team/?graph_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user, system_user):
        """Lines 247-253: GET exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.serialize_graph_team",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/graph-team/?graph_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestDashboardViewExtra:
    """DashboardView extra coverage."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 273-279: GET access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/dashboard/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user, system_user):
        """Lines 280-287: GET exception (user_id=-1)."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.get_dashboard",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/dashboard/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_access_denied(self, api_client, test_user):
        """Lines 307-313: POST access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.post(
                f"{BASE}/dashboard/",
                {"season_id": 1, "default_dash_view_typ": "grid", "dashboard_views": []},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_post_exception(self, api_client, test_user):
        """Lines 314-321: POST exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.save_dashboard",
                   side_effect=Exception("boom")):
            response = api_client.post(
                f"{BASE}/dashboard/",
                {"season_id": 1, "default_dash_view_typ": "grid", "dashboard_views": []},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestDashboardViewTypeViewExtra:
    """DashboardViewTypeView extra coverage."""

    def test_get_access_denied(self, api_client, test_user):
        """Lines 340-345: GET access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=False):
            response = api_client.get(f"{BASE}/dashboard-view-types/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user, system_user):
        """Lines 346-352: GET exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.strategizing.views.has_access", return_value=True), \
             patch("scouting.strategizing.views.scouting.strategizing.util.get_dashboard_view_types",
                   side_effect=Exception("boom")):
            response = api_client.get(f"{BASE}/dashboard-view-types/")
        assert response.status_code == 200
        assert response.data.get("error") is True
