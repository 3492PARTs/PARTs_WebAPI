"""
Comprehensive tests for Scouting model __str__ methods to increase coverage.
"""
import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestScoutingModelStringMethods:
    """Test __str__ methods for scouting app models."""
    
    def test_season_str(self):
        """Test Season __str__ method."""
        from scouting.models import Season
        
        season = Season.objects.create(
            season="2024",
            current="y",
            game="Test Game",
            manual="https://manual.example.com"
        )
        str_result = str(season)
        assert str(season.id) in str_result
        assert "2024" in str_result
    
    def test_team_str(self):
        """Test Team __str__ method."""
        from scouting.models import Team
        
        team = Team.objects.create(
            team_no=3492,
            team_nm="PARTs"
        )
        str_result = str(team)
        assert "3492" in str_result
        assert "PARTs" in str_result
    
    def test_event_str(self):
        """Test Event __str__ method."""
        from scouting.models import Season, Event
        
        season = Season.objects.create(
            season="2024",
            current="y",
            game="Test Game",
            manual="https://manual.example.com"
        )
        
        event = Event.objects.create(
            season=season,
            event_nm="Test Competition",
            event_cd="2024test",
            date_st=timezone.now(),
            date_end=timezone.now()
        )
        str_result = str(event)
        assert str(event.id) in str_result
        assert "Test Competition" in str_result
    
    def test_event_team_info_str(self):
        """Test EventTeamInfo __str__ method."""
        from scouting.models import Season, Team, Event, EventTeamInfo
        
        season = Season.objects.create(
            season="2024",
            current="y",
            game="Test Game",
            manual="https://manual.example.com"
        )
        
        team = Team.objects.create(
            team_no=1234,
            team_nm="Test Team"
        )
        
        event = Event.objects.create(
            season=season,
            event_nm="Regional",
            event_cd="2024reg",
            date_st=timezone.now(),
            date_end=timezone.now()
        )
        
        team_info = EventTeamInfo.objects.create(
            event=event,
            team=team,
            rank=5
        )
        str_result = str(team_info)
        assert "Event:" in str_result
        assert "Team:" in str_result
    
    def test_competition_level_str(self):
        """Test CompetitionLevel __str__ method."""
        from scouting.models import CompetitionLevel
        
        comp_level = CompetitionLevel.objects.create(
            comp_lvl_typ="qual",
            comp_lvl_typ_nm="Qualification",
            comp_lvl_order=1
        )
        str_result = str(comp_level)
        assert "qual" in str_result
        assert "Qualification" in str_result


@pytest.mark.django_db
class TestScoutingModelDefaults:
    """Test scouting model default values."""
    
    def test_season_current_default(self):
        """Test Season current default value."""
        from scouting.models import Season
        
        season = Season.objects.create(
            season="2025",
            game="New Game",
            manual="https://manual.example.com"
        )
        assert season.current == "n"
    
    def test_team_void_default(self):
        """Test Team void_ind default value."""
        from scouting.models import Team
        
        team = Team.objects.create(
            team_no=9999,
            team_nm="Default Team"
        )
        assert team.void_ind == "n"
    
    def test_event_defaults(self):
        """Test Event default values."""
        from scouting.models import Season, Event
        
        season = Season.objects.create(
            season="2024",
            game="Test Game",
            manual="https://manual.example.com"
        )
        
        event = Event.objects.create(
            season=season,
            event_nm="Test Event",
            event_cd="2024evt",
            date_st=timezone.now(),
            date_end=timezone.now()
        )
        assert event.current == "n"
        assert event.competition_page_active == "n"
        assert event.void_ind == "n"
    
    def test_competition_level_void_default(self):
        """Test CompetitionLevel void_ind default value."""
        from scouting.models import CompetitionLevel
        
        comp_level = CompetitionLevel.objects.create(
            comp_lvl_typ="playoff",
            comp_lvl_typ_nm="Playoff",
            comp_lvl_order=2
        )
        assert comp_level.void_ind == "n"
