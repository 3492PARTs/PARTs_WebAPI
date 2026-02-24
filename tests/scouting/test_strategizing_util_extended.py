"""
Extended tests for scouting/strategizing/util.py to improve coverage.
Focuses on utility functions for team notes, match strategies, alliance selections, and graphing.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pytz


@pytest.mark.django_db
class TestGetTeamNotes:
    """Tests for get_team_notes function."""

    def test_get_team_notes_no_filters(self):
        """Test getting all team notes without filters."""
        from scouting.strategizing.util import get_team_notes
        from scouting.models import TeamNote, Team, Event, Season
        from user.models import User
        
        # Create necessary objects
        user = User.objects.create(username="testuser", email="test@example.com")
        season = Season.objects.create(season="2024", current="y", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Test Event",
            event_cd="test",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC)
        )
        team = Team.objects.create(team_no=3492, team_nm="Test Team")
        
        # Create a team note
        TeamNote.objects.create(
            event=event,
            team=team,
            user=user,
            note="Test note",
            void_ind="n"
        )
        
        result = get_team_notes()
        
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_team_notes_filter_by_event(self):
        """Test getting team notes filtered by event."""
        from scouting.strategizing.util import get_team_notes
        from scouting.models import Event, Season
        
        season = Season.objects.create(season="2026", current="n", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Test Event 3",
            event_cd="test3",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC)
        )
        
        result = get_team_notes(event=event)
        
        assert isinstance(result, list)


@pytest.mark.django_db
class TestParseTeamNote:
    """Tests for parse_team_note function."""

    def test_parse_team_note_with_match(self):
        """Test parsing a team note that has an associated match."""
        from scouting.strategizing.util import parse_team_note
        from scouting.models import TeamNote, Team, Event, Season, Match, CompetitionLevel
        from user.models import User
        
        # Create necessary objects
        user = User.objects.create(username="parseuser", email="parse@example.com")
        season = Season.objects.create(season="2027", current="n", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Parse Event",
            event_cd="parse",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC)
        )
        team = Team.objects.create(team_no=5678, team_nm="Parse Team")
        comp_level = CompetitionLevel.objects.get_or_create(
            comp_lvl_typ="qm",
            defaults={"comp_lvl_typ_nm": "Qualification", "comp_lvl_order": 1}
        )[0]
        match = Match.objects.create(
            match_key="2027parse_qm1",
            match_number=1,
            event=event,
            comp_level=comp_level
        )
        
        note = TeamNote.objects.create(
            event=event,
            team=team,
            match=match,
            user=user,
            note="Note with match",
            void_ind="n"
        )
        
        result = parse_team_note(note)
        
        assert result["id"] == note.id
        assert result["team_id"] == 5678
        assert result["match_id"] == "2027parse_qm1"
        assert result["note"] == "Note with match"
        assert result["user"] == user

    def test_parse_team_note_without_match(self):
        """Test parsing a team note without an associated match."""
        from scouting.strategizing.util import parse_team_note
        from scouting.models import TeamNote, Team, Event, Season
        from user.models import User
        
        # Create necessary objects
        user = User.objects.create(username="parseuser2", email="parse2@example.com")
        season = Season.objects.create(season="2028", current="n", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Parse Event 2",
            event_cd="parse2",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC)
        )
        team = Team.objects.create(team_no=9012, team_nm="Parse Team 2")
        
        note = TeamNote.objects.create(
            event=event,
            team=team,
            user=user,
            note="Note without match",
            void_ind="n"
        )
        
        result = parse_team_note(note)
        
        assert result["id"] == note.id
        assert result["match_id"] is None


@pytest.mark.django_db
class TestGetMatchStrategies:
    """Tests for get_match_strategies function."""

    def test_get_match_strategies_no_filters(self):
        """Test getting match strategies without filters."""
        from scouting.strategizing.util import get_match_strategies
        
        result = get_match_strategies()
        
        assert isinstance(result, list)

    def test_get_match_strategies_filter_by_event(self):
        """Test getting match strategies filtered by event."""
        from scouting.strategizing.util import get_match_strategies
        from scouting.models import Event, Season
        
        season = Season.objects.create(season="2030", current="n", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Strategy Event",
            event_cd="strat",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC)
        )
        
        result = get_match_strategies(event=event)
        
        assert isinstance(result, list)


@pytest.mark.django_db
class TestSaveMatchStrategy:
    """Tests for save_match_strategy function."""

    def test_save_match_strategy_new(self):
        """Test saving a new match strategy."""
        from scouting.strategizing.util import save_match_strategy
        from scouting.models import Event, Season, Match, CompetitionLevel
        from user.models import User
        
        # Create necessary objects
        user = User.objects.create(username="stratuser", email="strat@example.com")
        season = Season.objects.create(season="2031", current="n", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Strat Event",
            event_cd="strat2",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC)
        )
        comp_level = CompetitionLevel.objects.get_or_create(
            comp_lvl_typ="qm",
            defaults={"comp_lvl_typ_nm": "Qualification", "comp_lvl_order": 1}
        )[0]
        match = Match.objects.create(
            match_key="2031strat2_qm1",
            match_number=1,
            event=event,
            comp_level=comp_level
        )
        
        data = {
            "match_key": match.match_key,
            "user_id": user.id,
            "strategy": "Test strategy"
        }
        
        # Should not raise an exception
        save_match_strategy(data)
        
        # Verify it was saved
        from scouting.models import MatchStrategy
        assert MatchStrategy.objects.filter(
            match=match,
            user=user,
            strategy="Test strategy"
        ).exists()


@pytest.mark.django_db
class TestGetAllianceSelections:
    """Tests for get_alliance_selections function."""

    def test_get_alliance_selections(self):
        """Test getting alliance selections for current event."""
        from scouting.strategizing.util import get_alliance_selections
        from scouting.models import Event, Season
        
        # Create current event
        season = Season.objects.create(season="2032", current="y", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Alliance Event",
            event_cd="alliance",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC),
            current="y"
        )
        
        result = get_alliance_selections()
        
        assert result is not None


@pytest.mark.django_db
class TestSaveAllianceSelections:
    """Tests for save_alliance_selections function."""

    def test_save_alliance_selections_new(self):
        """Test saving new alliance selections."""
        from scouting.strategizing.util import save_alliance_selections
        from scouting.models import Event, Season, Team
        
        # Create necessary objects
        season = Season.objects.create(season="2033", current="n", game="Test", manual="")
        event = Event.objects.create(
            season=season,
            event_nm="Alliance Event 2",
            event_cd="alliance2",
            date_st=datetime.now(pytz.UTC),
            date_end=datetime.now(pytz.UTC)
        )
        team = Team.objects.create(team_no=7890, team_nm="Alliance Team")
        
        data = [
            {
                "event": {"id": event.id},
                "team": {"team_no": team.team_no},
                "note": "First pick",
                "order": 1
            }
        ]
        
        # Should not raise an exception
        save_alliance_selections(data)
        
        # Verify it was saved
        from scouting.models import AllianceSelection
        assert AllianceSelection.objects.filter(
            event=event,
            team=team,
            order=1
        ).exists()


@pytest.mark.django_db
class TestGetDashboardViewTypes:
    """Tests for get_dashboard_view_types function."""

    def test_get_dashboard_view_types(self):
        """Test getting dashboard view types."""
        from scouting.strategizing.util import get_dashboard_view_types
        from scouting.models import DashboardViewType
        
        # Create a dashboard view type with correct field name
        DashboardViewType.objects.create(
            dash_view_typ="test_type",
            dash_view_nm="Test Type"
        )
        
        result = get_dashboard_view_types()
        
        assert result is not None
        assert result.count() >= 1


@pytest.mark.django_db
class TestGraphTeam:
    """Tests for graph_team function."""

    def test_graph_team_function_exists(self):
        """Test that graph_team function exists and is callable."""
        from scouting.strategizing.util import graph_team
        
        # Just verify the function exists
        assert callable(graph_team)
