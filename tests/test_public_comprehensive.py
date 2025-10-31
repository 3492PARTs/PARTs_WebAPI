"""
Comprehensive tests for the public app modules (season and competition).

Tests cover:
- public.views.APIStatusView
- public.season.views.CurrentSeasonView
- public.competition.views.InitView  
- public.competition.util.get_competition_information()
- Serializers for both season and competition
"""

import pytest
from unittest.mock import patch, Mock
from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework import status

from scouting.models import Season, Event, Match, Team, CompetitionLevel
from public.views import APIStatusView
from public.season.views import CurrentSeasonView
from public.competition.views import InitView
from public.competition.util import get_competition_information
from public.competition.serializers import CompetitionInformationSerializer


@pytest.fixture
def api_rf():
    return APIRequestFactory()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def season(db):
    """Create a test season"""
    return Season.objects.create(
        season=2024,
        current="y"
    )


@pytest.fixture
def team_3492(db):
    """Create team 3492"""
    return Team.objects.create(
        team_no=3492,
        team_nm="PARTs",
        void_ind="n"
    )


@pytest.fixture
def comp_level(db):
    """Create competition level"""
    return CompetitionLevel.objects.create(
        comp_lvl_typ="qm",
        comp_lvl_typ_nm="Qualification",
        comp_lvl_order=1
    )


@pytest.fixture
def event(db, season):
    """Create a test event"""
    from django.utils.timezone import now
    return Event.objects.create(
        season=season,
        event_nm="Test Competition",
        event_cd="TEST2024",
        date_st=now(),
        date_end=now(),
        current="y",
        competition_page_active="y"
    )


@pytest.fixture
def other_team(db):
    """Create another team for matches"""
    return Team.objects.create(
        team_no=1234,
        team_nm="Other Team",
        void_ind="n"
    )


# ============================================================================
# public.views.APIStatusView Tests
# ============================================================================

@pytest.mark.django_db
class TestAPIStatusView:
    """Tests for the main APIStatusView"""
    
    def test_api_status_returns_environment_and_version(self, api_rf, test_user):
        """Test that API status returns environment branch and version"""
        request = api_rf.get('/api-status/')
        force_authenticate(request, user=test_user)
        
        view = APIStatusView.as_view()
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'branch' in response.data
        assert 'version' in response.data
    
    def test_api_status_without_authentication(self, api_rf):
        """Test API status works without authentication"""
        request = api_rf.get('/api-status/')
        
        view = APIStatusView.as_view()
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data is not None


# ============================================================================
# public.season.views.CurrentSeasonView Tests
# ============================================================================

@pytest.mark.django_db
class TestCurrentSeasonView:
    """Tests for CurrentSeasonView"""
    
    def test_current_season_view_success(self, api_rf, test_user, season):
        """Test getting current season successfully"""
        request = api_rf.get('/public/season/current/')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.get_current_season') as mock_get_season:
            mock_get_season.return_value = season
            
            view = CurrentSeasonView.as_view()
            response = view(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert 'season' in response.data
            mock_get_season.assert_called_once()
    
    def test_current_season_view_no_season(self, api_rf, test_user):
        """Test when no current season exists"""
        request = api_rf.get('/public/season/current/')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.get_current_season') as mock_get_season:
            mock_get_season.return_value = None
            
            view = CurrentSeasonView.as_view()
            response = view(request)
            
            assert response.status_code == status.HTTP_200_OK
    
    def test_current_season_view_exception_handling(self, api_rf, test_user):
        """Test exception handling in CurrentSeasonView"""
        request = api_rf.get('/public/season/current/')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.get_current_season') as mock_get_season:
            mock_get_season.side_effect = Exception("Database error")
            
            view = CurrentSeasonView.as_view()
            response = view(request)
            
            # Should return error message via ret_message
            assert response.status_code == status.HTTP_200_OK
            assert 'error' in response.data or 'message' in response.data


# ============================================================================
# public.competition.util Tests
# ============================================================================

@pytest.mark.django_db
class TestGetCompetitionInformation:
    """Tests for get_competition_information utility function"""
    
    def test_get_competition_information_success(self, event, team_3492, comp_level, other_team):
        """Test getting competition information with matches"""
        # Create some matches with team 3492
        match1 = Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level.comp_lvl_typ}1",
            event=event,
            comp_level=comp_level,
            match_number=1,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="n"
        )
        
        match2 = Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level.comp_lvl_typ}2",
            event=event,
            comp_level=comp_level,
            match_number=2,
            blue_one=team_3492,
            blue_two=other_team,
            blue_three=other_team,
            red_one=other_team,
            red_two=other_team,
            red_three=other_team,
            void_ind="n"
        )
        
        with patch('scouting.util.parse_match') as mock_parse:
            mock_parse.side_effect = lambda m: {'match_number': m.match_number}
            
            result = get_competition_information()
            
            assert result is not None
            assert 'event' in result
            assert 'matches' in result
            assert result['event'] == event
            assert len(result['matches']) == 2
            assert mock_parse.call_count == 2
    
    def test_get_competition_information_team_in_different_positions(self, event, team_3492, comp_level, other_team):
        """Test that matches are found regardless of team 3492's position"""
        positions = ['red_one', 'red_two', 'red_three', 'blue_one', 'blue_two', 'blue_three']
        
        for i, position in enumerate(positions):
            match_data = {
                'match_key': f"{event.event_cd}_{comp_level.comp_lvl_typ}{i + 1}",
                'event': event,
                'comp_level': comp_level,
                'match_number': i + 1,
                'void_ind': 'n',
                'red_one': other_team,
                'red_two': other_team,
                'red_three': other_team,
                'blue_one': other_team,
                'blue_two': other_team,
                'blue_three': other_team,
            }
            match_data[position] = team_3492
            Match.objects.create(**match_data)
        
        with patch('scouting.util.parse_match') as mock_parse:
            mock_parse.side_effect = lambda m: {'match_number': m.match_number}
            
            result = get_competition_information()
            
            assert len(result['matches']) == 6
    
    def test_get_competition_information_filters_void_matches(self, event, team_3492, comp_level, other_team):
        """Test that void matches are excluded"""
        # Create valid match
        Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level.comp_lvl_typ}1",
            event=event,
            comp_level=comp_level,
            match_number=1,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="n"
        )
        
        # Create void match
        Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level.comp_lvl_typ}2",
            event=event,
            comp_level=comp_level,
            match_number=2,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="y"  # Void
        )
        
        with patch('scouting.util.parse_match') as mock_parse:
            mock_parse.side_effect = lambda m: {'match_number': m.match_number}
            
            result = get_competition_information()
            
            # Should only include non-void match
            assert len(result['matches']) == 1
    
    def test_get_competition_information_orders_by_comp_level_and_number(self, event, team_3492, other_team):
        """Test that matches are ordered correctly"""
        comp_level_qual = CompetitionLevel.objects.create(
            comp_lvl_typ="qm",
            comp_lvl_typ_nm="Qualification",
            comp_lvl_order=1
        )
        
        comp_level_playoff = CompetitionLevel.objects.create(
            comp_lvl_typ="sf",
            comp_lvl_typ_nm="Semifinal",
            comp_lvl_order=2
        )
        
        # Create matches out of order
        Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level_playoff.comp_lvl_typ}1",
            event=event,
            comp_level=comp_level_playoff,
            match_number=1,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="n"
        )
        
        Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level_qual.comp_lvl_typ}2",
            event=event,
            comp_level=comp_level_qual,
            match_number=2,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="n"
        )
        
        Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level_qual.comp_lvl_typ}1",
            event=event,
            comp_level=comp_level_qual,
            match_number=1,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="n"
        )
        
        with patch('scouting.util.parse_match') as mock_parse:
            mock_parse.side_effect = lambda m: {
                'comp_level_order': m.comp_level.comp_lvl_order,
                'match_number': m.match_number
            }
            
            result = get_competition_information()
            
            # Should be ordered: qm-1, qm-2, sf-1
            assert len(result['matches']) == 3
            assert result['matches'][0]['match_number'] == 1
            assert result['matches'][0]['comp_level_order'] == 1
            assert result['matches'][1]['match_number'] == 2
            assert result['matches'][1]['comp_level_order'] == 1
            assert result['matches'][2]['match_number'] == 1
            assert result['matches'][2]['comp_level_order'] == 2
    
    def test_get_competition_information_no_current_event(self, db):
        """Test when no current event with competition page active exists"""
        from django.utils.timezone import now
        # Create event but not current
        season = Season.objects.create(season=2024, current="y")
        Event.objects.create(
            season=season,
            event_nm="Past Event",
            event_cd="PAST2024",
            date_st=now(),
            date_end=now(),
            current="n",  # Not current
            competition_page_active="y"
        )
        
        Team.objects.create(team_no=3492, team_nm="PARTs")
        
        with pytest.raises(Event.DoesNotExist):
            get_competition_information()
    
    def test_get_competition_information_competition_page_not_active(self, db):
        """Test when event exists but competition page is not active"""
        from django.utils.timezone import now
        season = Season.objects.create(season=2024, current="y")
        Event.objects.create(
            season=season,
            event_nm="Test Event",
            event_cd="TEST2024",
            date_st=now(),
            date_end=now(),
            current="y",
            competition_page_active="n"  # Not active
        )
        
        Team.objects.create(team_no=3492, team_nm="PARTs")
        
        with pytest.raises(Event.DoesNotExist):
            get_competition_information()


# ============================================================================
# public.competition.views.InitView Tests
# ============================================================================

@pytest.mark.django_db
class TestInitView:
    """Tests for competition InitView"""
    
    def test_init_view_success(self, api_rf, test_user, event, team_3492, comp_level, other_team):
        """Test successful competition init response"""
        # Create a match
        Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level.comp_lvl_typ}1",
            event=event,
            comp_level=comp_level,
            match_number=1,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="n"
        )
        
        request = api_rf.get('/public/competition/init/')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.util.parse_match') as mock_parse:
            mock_parse.return_value = {'match_number': 1}
            
            view = InitView.as_view()
            response = view(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert 'event' in response.data
            assert 'matches' in response.data
    
    def test_init_view_no_event(self, api_rf, test_user, db):
        """Test InitView when no event is available"""
        # Create team 3492 but no event
        Team.objects.create(team_no=3492, team_nm="PARTs", void_ind="n")
        
        request = api_rf.get('/public/competition/init/')
        force_authenticate(request, user=test_user)
        
        view = InitView.as_view()
        response = view(request)
        
        # Should return "No event" message
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data or 'error' in response.data
    
    def test_init_view_exception_handling(self, api_rf, test_user):
        """Test exception handling in InitView"""
        request = api_rf.get('/public/competition/init/')
        force_authenticate(request, user=test_user)
        
        with patch('public.competition.util.get_competition_information') as mock_get_info:
            mock_get_info.side_effect = Exception("Unexpected error")
            
            view = InitView.as_view()
            response = view(request)
            
            # Should handle exception gracefully
            assert response.status_code == status.HTTP_200_OK
            assert 'message' in response.data or 'error' in response.data


# ============================================================================
# Serializer Tests
# ============================================================================

@pytest.mark.django_db
class TestCompetitionInformationSerializer:
    """Tests for CompetitionInformationSerializer"""
    
    def test_serializer_with_event_and_matches(self, event, team_3492, comp_level, other_team):
        """Test serializer with full competition information"""
        match = Match.objects.create(
            match_key=f"{event.event_cd}_{comp_level.comp_lvl_typ}1",
            event=event,
            comp_level=comp_level,
            match_number=1,
            red_one=team_3492,
            red_two=other_team,
            red_three=other_team,
            blue_one=other_team,
            blue_two=other_team,
            blue_three=other_team,
            void_ind="n"
        )
        
        data = {
            'event': event,
            'matches': [match]
        }
        
        serializer = CompetitionInformationSerializer(data)
        
        assert 'event' in serializer.data
        assert 'matches' in serializer.data
        assert len(serializer.data['matches']) == 1
    
    def test_serializer_with_event_no_matches(self, event):
        """Test serializer with event but no matches"""
        data = {
            'event': event,
            'matches': []
        }
        
        serializer = CompetitionInformationSerializer(data)
        
        assert 'event' in serializer.data
        assert 'matches' in serializer.data
        assert len(serializer.data['matches']) == 0
