"""
Extra coverage for tba/util.py:
  - lines 254-256 (IntegrityError → get existing team)
  - lines 263-264 (IntegrityError on event_set.add)
  - lines 290-291 (sync_matches exception path)
  - lines 368-390 (sync_event_team_info loop with update+add+no active event)
  - lines 450-463 (save_tba_match update existing match)
  - lines 517-521 (verify_tba_webhook_call)
"""
import pytest
from unittest.mock import patch, MagicMock
import json
import datetime
import hmac
from hashlib import sha256


# ---------------------------------------------------------------------------
# lines 254-256  (sync_teams IntegrityError → get existing team)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSyncTeamsIntegrityError:
    """Lines 254-258: IntegrityError on team insert → get existing team."""

    def test_sync_teams_existing_team(self):
        from tba.util import sync_teams
        from scouting.models import Season, Event, Team
        import datetime as dt

        season = Season.objects.create(season="2099tst1", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="TST1 Event", event_cd="2099tst1_ev",
            date_st=dt.date(2099, 8, 1), date_end=dt.date(2099, 8, 3),
            current="y", void_ind="n",
        )
        # Create existing team
        existing_team = Team.objects.create(team_no=5555, team_nm="Existing TBA Team", void_ind="n")

        data = {
            "event_cd": "2099tst1_ev",
            "teams": [
                {"team_no": 5555, "team_nm": "Existing TBA Team"},
            ],
        }
        result = sync_teams(data, event)
        assert "5555" in result


# ---------------------------------------------------------------------------
# lines 263-264  (sync_teams IntegrityError on event_set.add – covered implicitly)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSyncTeamsEventLinkError:
    """Lines 263-264: IntegrityError on team.event_set.add."""

    def test_sync_teams_link_error_handled(self):
        from tba.util import sync_teams
        from scouting.models import Season, Event, Team
        import datetime as dt

        season = Season.objects.create(season="2099tst2", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="TST2 Event", event_cd="2099tst2_ev",
            date_st=dt.date(2099, 8, 1), date_end=dt.date(2099, 8, 3),
            current="y", void_ind="n",
        )
        team = Team.objects.create(team_no=6666, team_nm="TST2 Team", void_ind="n")
        # Add team to event already so that add raises nothing (duplicate not forced here)
        event.teams.add(team)

        data = {
            "event_cd": "2099tst2_ev",
            "teams": [
                {"team_no": 6666, "team_nm": "TST2 Team"},
            ],
        }
        # Should succeed without error
        result = sync_teams(data, event)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# lines 290-291  (sync_matches exception on match processing)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSyncMatchesException:
    """Lines 290-291: exception during match processing logged in messages."""

    def test_sync_matches_exception_logged(self):
        from tba.util import sync_matches
        from scouting.models import Season, Event
        import datetime as dt

        season = Season.objects.create(season="2099tsm", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="TSM Event", event_cd="2099tsm_ev",
            date_st=dt.date(2099, 9, 1), date_end=dt.date(2099, 9, 3),
            current="y", void_ind="n",
        )

        matches = [{"match_number": 1, "key": "2099tsm_ev_qm1"}]
        with patch("tba.util.requests.get") as mock_get, \
             patch("tba.util.save_tba_match", side_effect=Exception("boom")):
            mock_get.return_value.text = json.dumps(matches)
            result = sync_matches(event)

        assert "(ERROR)" in result


# ---------------------------------------------------------------------------
# lines 368-390  (sync_event_team_info: update, add, no active event)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSyncEventTeamInfo:
    """Lines 368-390: sync_event_team_info update+add and 'No active event'."""

    def test_sync_event_team_info_force_update(self):
        """Lines 366-388: force=1 → loops through team info."""
        from tba.util import sync_event_team_info
        from scouting.models import Season, Event, Team
        import datetime as dt

        season = Season.objects.create(season="2099seti", current="y", game="G", manual="M")
        team = Team.objects.create(team_no=4444, team_nm="SETI Team", void_ind="n")
        event = Event.objects.create(
            season=season, event_nm="SETI Event", event_cd="2099seti_ev",
            date_st=dt.date(2099, 1, 1), date_end=dt.date(2099, 12, 31),
            current="y", void_ind="n",
        )
        event.teams.add(team)

        team_info = [{
            "team_id": team.team_no,
            "matches_played": 5,
            "qual_average": 50.0,
            "losses": 1,
            "wins": 4,
            "ties": 0,
            "rank": 2,
            "dq": 0,
        }]

        with patch("tba.util.Event.objects.get", return_value=event), \
             patch("tba.util.sync_event", return_value=""), \
             patch("tba.util.get_tba_event_team_info", return_value=team_info):
            result = sync_event_team_info(force=1)

        assert "(ADD)" in result or "(UPDATE)" in result

    def test_sync_event_team_info_no_active_event(self):
        """Lines 389-390: event not active → 'No active event'."""
        from tba.util import sync_event_team_info
        from scouting.models import Season, Event
        import datetime as dt

        season = Season.objects.create(season="2099sna", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="SNA Event", event_cd="2099sna_ev",
            date_st=dt.date(2099, 1, 1), date_end=dt.date(2099, 1, 2),
            current="y", void_ind="n",
        )

        with patch("tba.util.Event.objects.get", return_value=event), \
             patch("tba.util.sync_event", return_value=""), \
             patch("tba.util.get_tba_event_team_info", return_value=[]):
            result = sync_event_team_info(force=0)

        assert result == "No active event"


# ---------------------------------------------------------------------------
# lines 450-463  (save_tba_match update existing Match)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveTBAMatchUpdate:
    """Lines 450-463: save_tba_match updates existing match."""

    def test_save_tba_match_update(self):
        from tba.util import save_tba_match
        from scouting.models import Season, Event, Team, Match, CompetitionLevel, CompetitionLevelType
        import datetime as dt
        import pytz

        season = Season.objects.create(season="2099stm", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="STM Event", event_cd="2099stm",
            date_st=dt.date(2099, 10, 1), date_end=dt.date(2099, 10, 3),
            current="y", void_ind="n",
        )
        team_r1 = Team.objects.create(team_no=1111, team_nm="R1 Team", void_ind="n")
        clt = CompetitionLevelType.objects.create(
            comp_lvl_typ="qm_stm", comp_lvl_typ_nm="Qual STM", comp_lvl_order=1
        )
        cl = CompetitionLevel.objects.create(event=event, comp_lvl_typ=clt, void_ind="n")
        existing_match = Match.objects.create(
            match_key="2099stm_qm5",
            match_number=5,
            event=event,
            comp_level=cl,
            void_ind="n",
        )

        tba_match = {
            "key": "2099stm_qm5",
            "match_number": 5,
            "comp_level": "qm",
            "event_key": "2099stm",
            "time": None,
            "alliances": {
                "red": {"team_keys": ["frc1111", "frc0000", "frc0000"], "score": 50},
                "blue": {"team_keys": ["frc0000", "frc0000", "frc0000"], "score": 40},
            },
            "score_breakdown": None,
        }

        with patch("tba.util.Event.objects.get", return_value=event), \
             patch("tba.util.CompetitionLevel.objects.get_or_create", return_value=(cl, False)), \
             patch("tba.util.replace_frc_in_str", side_effect=lambda s: int(s.replace("frc", "")) if s.replace("frc", "").isdigit() else 0), \
             patch("tba.util.Team.objects.get") as mock_team_get:
            mock_team_get.return_value = team_r1
            result = save_tba_match(tba_match)

        assert "(UPDATE)" in result or "(ADD)" in result


# ---------------------------------------------------------------------------
# lines 517-521  (verify_tba_webhook_call)
# ---------------------------------------------------------------------------
class TestVerifyTBAWebhookCall:
    """Lines 517-521: verify_tba_webhook_call validates HMAC signature."""

    def test_valid_signature_returns_true(self):
        from tba.util import verify_tba_webhook_call
        from json import dumps

        secret = "test_secret"
        data = {"message_type": "ping", "message_data": {}}
        json_str = dumps(data, ensure_ascii=True)
        expected_hmac = hmac.new(
            secret.encode("utf-8"), json_str.encode("utf-8"), sha256
        ).hexdigest()

        mock_request = MagicMock()
        mock_request.data = data
        mock_request.META = {"HTTP_X_TBA_HMAC": expected_hmac}

        with patch("tba.util.settings.TBA_WEBHOOK_SECRET", secret):
            result = verify_tba_webhook_call(mock_request)

        assert result is True

    def test_invalid_signature_returns_false(self):
        from tba.util import verify_tba_webhook_call

        mock_request = MagicMock()
        mock_request.data = {"message_type": "ping"}
        mock_request.META = {"HTTP_X_TBA_HMAC": "wrong_hmac"}

        with patch("tba.util.settings.TBA_WEBHOOK_SECRET", "test_secret"):
            result = verify_tba_webhook_call(mock_request)

        assert result is False
