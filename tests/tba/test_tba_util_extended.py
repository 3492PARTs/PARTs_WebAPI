"""
Extended tests for TBA (The Blue Alliance) API integration in tba/util.py.
Tests cover sync operations, team retrieval, and match processing.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.db import IntegrityError
import json
import datetime
import pytz


@pytest.mark.django_db
class TestTBATeamRetrieval:
    """Tests for getting event teams from TBA."""

    def test_get_tba_event_teams_success(self):
        """Test successful retrieval of teams for an event."""
        from tba.util import get_tba_event_teams
        
        mock_teams = [
            {
                'team_number': 3492,
                'nickname': 'PARTs',
                'city': 'Test City',
                'state_prov': 'PA'
            },
            {
                'team_number': 341,
                'nickname': 'Miss Daisy',
                'city': 'Another City',
                'state_prov': 'PA'
            }
        ]
        
        with patch('tba.util.requests.get') as mock_get:
            mock_get.return_value.text = json.dumps(mock_teams)
            
            result = get_tba_event_teams('2024pahat')
            
            assert len(result) == 2
            assert result[0]['team_no'] == 3492
            assert result[0]['team_nm'] == 'PARTs'
            assert result[1]['team_no'] == 341
            assert result[1]['team_nm'] == 'Miss Daisy'

    def test_get_tba_event_teams_empty(self):
        """Test retrieval when no teams are at the event."""
        from tba.util import get_tba_event_teams
        
        with patch('tba.util.requests.get') as mock_get:
            mock_get.return_value.text = json.dumps([])
            
            result = get_tba_event_teams('2024empty')
            
            assert len(result) == 0


@pytest.mark.django_db
class TestSyncEvent:
    """Tests for synchronizing events from TBA."""

    def test_sync_event_new_event(self):
        """Test syncing a new event that doesn't exist in database."""
        from tba.util import sync_event
        from scouting.models import Season, Event
        
        season = Season.objects.create(
            season='2024',
            game='Test Game',
            manual='Test Manual'
        )
        
        mock_event_data = {
            'event_nm': 'Hatboro-Horsham',
            'date_st': datetime.datetime(2024, 3, 15, tzinfo=pytz.timezone('America/New_York')),
            'date_end': datetime.datetime(2024, 3, 17, tzinfo=pytz.timezone('America/New_York')),
            'event_cd': '2024pahat',
            'event_url': 'http://test.com',
            'gmaps_url': 'http://maps.google.com',
            'address': '123 Test St',
            'city': 'Hatboro',
            'state_prov': 'PA',
            'postal_code': '19040',
            'location_name': 'High School',
            'timezone': 'America/New_York',
            'webcast_url': 'http://webcast.com'
        }
        
        mock_teams = [
            {'team_no': 3492, 'team_nm': 'PARTs'}
        ]
        
        with patch('tba.util.get_tba_event', return_value=mock_event_data), \
             patch('tba.util.get_tba_event_teams', return_value=mock_teams):
            
            result = sync_event(season, '2024pahat')
            
            # Verify event was added
            assert '(ADD) Added event: 2024pahat' in result
            assert Event.objects.filter(event_cd='2024pahat').exists()
            
            # Verify event details
            event = Event.objects.get(event_cd='2024pahat')
            assert event.event_nm == 'Hatboro-Horsham'
            assert event.timezone == 'America/New_York'

    def test_sync_event_existing_event(self):
        """Test syncing an event that already exists."""
        from tba.util import sync_event
        from scouting.models import Season, Event
        
        season = Season.objects.create(
            season='2024',
            game='Test Game',
            manual='Test Manual'
        )
        
        # Create existing event
        existing_event = Event.objects.create(
            event_cd='2024pahat',
            season=season,
            event_nm='Old Name',
            date_st=datetime.datetime(2024, 3, 1, tzinfo=pytz.UTC),
            date_end=datetime.datetime(2024, 3, 3, tzinfo=pytz.UTC),
            void_ind='n'
        )
        
        mock_event_data = {
            'event_nm': 'Updated Name',
            'date_st': datetime.datetime(2024, 3, 15, tzinfo=pytz.timezone('America/New_York')),
            'date_end': datetime.datetime(2024, 3, 17, tzinfo=pytz.timezone('America/New_York')),
            'event_cd': '2024pahat',
            'event_url': 'http://test.com',
            'gmaps_url': None,
            'address': None,
            'city': None,
            'state_prov': None,
            'postal_code': None,
            'location_name': None,
            'timezone': 'America/New_York',
            'webcast_url': ''
        }
        
        with patch('tba.util.get_tba_event', return_value=mock_event_data), \
             patch('tba.util.get_tba_event_teams', return_value=[]):
            
            result = sync_event(season, '2024pahat')
            
            # Verify event was updated, not added
            assert '(NO ADD) Already have event: 2024pahat' in result
            
            # Verify event was updated
            existing_event.refresh_from_db()
            assert existing_event.event_nm == 'Updated Name'

    def test_sync_event_with_teams(self):
        """Test syncing event with teams."""
        from tba.util import sync_event
        from scouting.models import Season, Team
        
        season = Season.objects.create(
            season='2024',
            game='Test Game',
            manual='Test Manual'
        )
        
        mock_event_data = {
            'event_nm': 'Test Event',
            'date_st': datetime.datetime(2024, 3, 15, tzinfo=pytz.timezone('America/New_York')),
            'date_end': datetime.datetime(2024, 3, 17, tzinfo=pytz.timezone('America/New_York')),
            'event_cd': '2024test',
            'event_url': None,
            'gmaps_url': None,
            'address': None,
            'city': None,
            'state_prov': None,
            'postal_code': None,
            'location_name': None,
            'timezone': 'America/New_York',
            'webcast_url': ''
        }
        
        mock_teams = [
            {'team_no': 3492, 'team_nm': 'PARTs'},
            {'team_no': 341, 'team_nm': 'Miss Daisy'}
        ]
        
        with patch('tba.util.get_tba_event', return_value=mock_event_data), \
             patch('tba.util.get_tba_event_teams', return_value=mock_teams):
            
            result = sync_event(season, '2024test')
            
            # Verify teams were added
            assert '(ADD) Added team: 3492 PARTs' in result
            assert '(ADD) Added team: 341 Miss Daisy' in result
            assert '(LINK) Added team: 3492 PARTs to event: 2024test' in result
            
            # Verify teams exist
            assert Team.objects.filter(team_no=3492).exists()
            assert Team.objects.filter(team_no=341).exists()

    def test_sync_event_remove_team(self):
        """Test syncing event removes teams no longer at event."""
        from tba.util import sync_event
        from scouting.models import Season, Team, Event
        
        season = Season.objects.create(
            season='2024',
            game='Test Game',
            manual='Test Manual'
        )
        
        # Create event and team
        event = Event.objects.create(
            event_cd='2024test',
            season=season,
            event_nm='Test Event',
            date_st=datetime.datetime(2024, 3, 1, tzinfo=pytz.UTC),
            date_end=datetime.datetime(2024, 3, 3, tzinfo=pytz.UTC),
            void_ind='n'
        )
        
        team = Team.objects.create(
            team_no=1234,
            team_nm='Old Team',
            void_ind='n'
        )
        team.event_set.add(event)
        
        mock_event_data = {
            'event_nm': 'Test Event',
            'date_st': datetime.datetime(2024, 3, 15, tzinfo=pytz.timezone('America/New_York')),
            'date_end': datetime.datetime(2024, 3, 17, tzinfo=pytz.timezone('America/New_York')),
            'event_cd': '2024test',
            'event_url': None,
            'gmaps_url': None,
            'address': None,
            'city': None,
            'state_prov': None,
            'postal_code': None,
            'location_name': None,
            'timezone': 'America/New_York',
            'webcast_url': ''
        }
        
        # New teams list doesn't include 1234
        mock_teams = [
            {'team_no': 3492, 'team_nm': 'PARTs'}
        ]
        
        with patch('tba.util.get_tba_event', return_value=mock_event_data), \
             patch('tba.util.get_tba_event_teams', return_value=mock_teams):
            
            result = sync_event(season, '2024test')
            
            # Verify team was removed from event
            assert '(REMOVE) Removed team: 1234 Old Team from event: 2024test' in result
            
            # Team should still exist but not be linked to event
            assert Team.objects.filter(team_no=1234).exists()
            team.refresh_from_db()
            assert event not in team.event_set.all()


@pytest.mark.django_db
class TestSyncSeason:
    """Tests for synchronizing entire seasons from TBA."""

    def test_sync_season_success(self):
        """Test successful season sync."""
        from tba.util import sync_season
        from scouting.models import Season
        
        season = Season.objects.create(
            season='2024',
            game='Test Game',
            manual='Test Manual'
        )
        
        mock_events = [
            {'key': '2024pahat'},
            {'key': '2024papit'}
        ]
        
        with patch('tba.util.requests.get') as mock_get, \
             patch('tba.util.sync_event', return_value='Synced event\n'):
            
            mock_get.return_value.text = json.dumps(mock_events)
            
            result = sync_season(season.id)
            
            # Should have synced both events
            assert 'Synced event' in result
            assert '------------------------------------------------' in result

    def test_sync_season_no_events(self):
        """Test season sync when no events exist."""
        from tba.util import sync_season
        from scouting.models import Season
        
        season = Season.objects.create(
            season='2024',
            game='Test Game',
            manual='Test Manual'
        )
        
        with patch('tba.util.requests.get') as mock_get:
            mock_get.return_value.text = json.dumps([])
            
            result = sync_season(season.id)
            
            # Should return empty messages
            assert result == ''


@pytest.mark.django_db
class TestGetMatchesForTeamEvent:
    """Tests for getting matches for a team at an event."""

    def test_get_matches_for_team_event_success(self):
        """Test successful match retrieval."""
        from tba.util import get_matches_for_team_event
        
        mock_matches = [
            {
                'key': '2024pahat_qm1',
                'match_number': 1,
                'alliances': {
                    'red': {'team_keys': ['frc3492', 'frc341', 'frc1']},
                    'blue': {'team_keys': ['frc2', 'frc3', 'frc4']}
                }
            },
            {
                'key': '2024pahat_qm2',
                'match_number': 2,
                'alliances': {
                    'red': {'team_keys': ['frc5', 'frc6', 'frc7']},
                    'blue': {'team_keys': ['frc3492', 'frc8', 'frc9']}
                }
            }
        ]
        
        with patch('tba.util.requests.get') as mock_get:
            mock_get.return_value.text = json.dumps(mock_matches)
            
            result = get_matches_for_team_event('3492', '2024pahat')
            
            assert len(result) == 2
            assert result[0]['key'] == '2024pahat_qm1'
            assert result[1]['match_number'] == 2

    def test_get_matches_for_team_event_no_matches(self):
        """Test when team has no matches at event."""
        from tba.util import get_matches_for_team_event
        
        with patch('tba.util.requests.get') as mock_get:
            mock_get.return_value.text = json.dumps([])
            
            result = get_matches_for_team_event('3492', '2024test')
            
            assert len(result) == 0


@pytest.mark.django_db
class TestGetEventsForTeam:
    """Tests for get_events_for_team function."""

    def test_get_events_for_team_with_ignore_list(self):
        """Test getting events with ignore list."""
        from tba.util import get_events_for_team
        from scouting.models import Team, Season
        
        team = Team.objects.create(team_no=3492, team_nm='PARTs')
        season = Season.objects.create(season='2024', game='Test', manual='Manual')
        
        mock_events = [
            {'key': '2024pahat'},
            {'key': '2024papit'},
            {'key': '2024paignore'}
        ]
        
        mock_event_data = {
            'event_nm': 'Test Event',
            'event_cd': '2024pahat',
            'date_st': datetime.datetime(2024, 3, 15, tzinfo=pytz.UTC),
            'date_end': datetime.datetime(2024, 3, 17, tzinfo=pytz.UTC),
            'timezone': 'America/New_York',
            'webcast_url': ''
        }
        
        with patch('tba.util.requests.get') as mock_get, \
             patch('tba.util.get_tba_event', return_value=mock_event_data):
            
            mock_get.return_value.text = json.dumps(mock_events)
            
            result = get_events_for_team(team, season, ['2024paignore'])
            
            # Should have 3 events but ignored one should only have event_cd
            assert len(result) == 3
            assert result[2]['event_cd'] == '2024paignore'
            # Other events should have full data
            assert result[0]['event_nm'] == 'Test Event'

    def test_get_events_for_team_no_ignore(self):
        """Test getting events without ignore list."""
        from tba.util import get_events_for_team
        from scouting.models import Team, Season
        
        team = Team.objects.create(team_no=3492, team_nm='PARTs')
        season = Season.objects.create(season='2024', game='Test', manual='Manual')
        
        mock_events = [
            {'key': '2024pahat'}
        ]
        
        mock_event_data = {
            'event_nm': 'Hatboro',
            'event_cd': '2024pahat',
            'date_st': datetime.datetime(2024, 3, 15, tzinfo=pytz.UTC),
            'date_end': datetime.datetime(2024, 3, 17, tzinfo=pytz.UTC),
            'timezone': 'America/New_York',
            'webcast_url': ''
        }
        
        with patch('tba.util.requests.get') as mock_get, \
             patch('tba.util.get_tba_event', return_value=mock_event_data):
            
            mock_get.return_value.text = json.dumps(mock_events)
            
            result = get_events_for_team(team, season, None)
            
            assert len(result) == 1
            assert result[0]['event_nm'] == 'Hatboro'
