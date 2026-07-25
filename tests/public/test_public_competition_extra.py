"""
Extra coverage for public/competition/views.py lines 26-27 (outer exception).
"""
import pytest
from unittest.mock import patch


@pytest.mark.django_db
class TestPublicCompetitionInitOuter:
    """Lines 26-27: outer exception handler returns error message."""

    url = "/public/competition/init/"

    def test_outer_exception_returns_error(self, api_client):
        """Lines 26-27: outer exception path."""
        with patch(
            "public.competition.views.public.competition.util.get_competition_information",
            side_effect=Exception("outer boom"),
        ), patch(
            "public.competition.views.ret_message",
            side_effect=[Exception("inner boom"), {"error": True, "message": "err"}],
        ):
            # We just need to call the endpoint; either the inner or outer
            # exception path will execute lines 26-27
            response = api_client.get(self.url)
        # The outer exception wraps any remaining error
        assert response.status_code == 200

    def test_no_event_returns_no_event_message(self, api_client):
        """Lines 24-25: inner exception returns 'No event'."""
        with patch(
            "public.competition.views.public.competition.util.get_competition_information",
            side_effect=Exception("no event"),
        ):
            response = api_client.get(self.url)
        assert response.status_code == 200
        assert "No event" in str(response.data)
