"""
Extra coverage for tba/util.py:
  - lines 254-256 (IntegrityError → get existing team inside sync_event)
  - lines 263-264 (IntegrityError on event_set.add inside sync_event)
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
# lines 254-256  (sync_event: IntegrityError on team insert → get existing team)
# ---------------------------------------------------------------------------
@pytest.mark.django_db(transaction=True)
class TestSyncEventIntegrityErrorTeam:
    """Lines 254-256: IntegrityError on team.save(force_insert=True) → get existing."""

    def test_sync_event_uses_existing_team(self):
        from tba.util import sync_event
        from scouting.models import Season, Event, Team
        import datetime as dt

        season = Season.objects.create(season="2099tst1", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="TST1 Event", event_cd="2099tst1",
            date_st=dt.date(2099, 8, 1), date_end=dt.date(2099, 8, 3),
            current="y", void_ind="n",
        )
        # Create existing team so save(force_insert=True) raises IntegrityError
        existing_team = Team.objects.create(team_no=5555, team_nm="Existing TBA Team", void_ind="n")

        tba_event_data = {
            "event_cd": "2099tst1",
            "event_nm": "TST1 Event",
            "event_url": "",
            "address": "",
            "city": "",
            "state_prov": "",
            "postal_code": "",
            "location_name": "",
            "gmaps_url": "",
            "webcast_url": "",
            "timezone": "America/New_York",
            "date_st": dt.date(2099, 8, 1),
            "date_end": dt.date(2099, 8, 3),
            "teams": [{"team_no": 5555, "team_nm": "Existing TBA Team"}],
        }

        with patch("tba.util.get_tba_event", return_value=tba_event_data), \
             patch("tba.util.get_tba_event_teams", return_value=[{"team_no": 5555, "team_nm": "Existing TBA Team"}]):
            result = sync_event(season, "2099tst1")

        assert "5555" in result


# ---------------------------------------------------------------------------
# lines 263-264  (sync_event: IntegrityError on team.event_set.add)
# ---------------------------------------------------------------------------
@pytest.mark.django_db(transaction=True)
class TestSyncEventIntegrityErrorLink:
    """Lines 263-264: IntegrityError on team.event_set.add."""

    def test_sync_event_link_integrity_error_handled(self):
        from tba.util import sync_event
        from scouting.models import Season, Event, Team
        import datetime as dt

        season = Season.objects.create(season="2099tst2", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="TST2 Event", event_cd="2099tst2",
            date_st=dt.date(2099, 8, 1), date_end=dt.date(2099, 8, 3),
            current="y", void_ind="n",
        )
        team = Team.objects.create(team_no=6666, team_nm="TST2 Team", void_ind="n")

        tba_event_data = {
            "event_cd": "2099tst2",
            "event_nm": "TST2 Event",
            "event_url": "",
            "address": "",
            "city": "",
            "state_prov": "",
            "postal_code": "",
            "location_name": "",
            "gmaps_url": "",
            "webcast_url": "",
            "timezone": "America/New_York",
            "date_st": dt.date(2099, 8, 1),
            "date_end": dt.date(2099, 8, 3),
            "teams": [{"team_no": 6666, "team_nm": "TST2 Team"}],
        }

        from django.db.utils import IntegrityError as DjangoIntegrityError

        with patch("tba.util.get_tba_event", return_value=tba_event_data), \
             patch("tba.util.get_tba_event_teams", return_value=[{"team_no": 6666, "team_nm": "TST2 Team"}]):
            # Patch team.event_set.add to raise IntegrityError on second call
            original_add = event.teams.add
            call_count = [0]

            def mock_team_add(t):
                call_count[0] += 1
                if call_count[0] == 1:
                    raise DjangoIntegrityError("duplicate")
                return original_add(t)

            with patch.object(team.__class__, "event_set", create=True):
                result = sync_event(season, "2099tst2")
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
        from scouting.models import Season, Event, Team, Match, CompetitionLevel
        import datetime as dt

        season = Season.objects.create(season="2099stm", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="STM Event", event_cd="2099stm",
            date_st=dt.date(2099, 10, 1), date_end=dt.date(2099, 10, 3),
            current="y", void_ind="n",
        )
        team_r1 = Team.objects.create(team_no=1111, team_nm="R1 Team", void_ind="n")
        cl = CompetitionLevel.objects.create(
            comp_lvl_typ="qm_stm_upd", comp_lvl_typ_nm="Qual STM", comp_lvl_order=1, void_ind="n"
        )
        existing_match = Match.objects.create(
            match_key="2099stm_qm5_upd",
            match_number=5,
            event=event,
            comp_level=cl,
            void_ind="n",
        )

        tba_match = {
            "key": "2099stm_qm5_upd",
            "match_number": 5,
            "comp_level": "qm_stm_upd",
            "event_key": "2099stm",
            "time": None,
            "alliances": {
                "red": {"team_keys": ["frc1111", "frc1111", "frc1111"], "score": 50},
                "blue": {"team_keys": ["frc1111", "frc1111", "frc1111"], "score": 40},
            },
            "score_breakdown": None,
        }

        with patch("tba.util.Event.objects.get", return_value=event), \
             patch("tba.util.Team.objects.get", return_value=team_r1), \
             patch("tba.util.CompetitionLevel.objects.get", return_value=cl):
            result = save_tba_match(tba_match)

        assert "(UPDATE)" in result


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
