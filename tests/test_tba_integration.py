"""
Complex integration tests for The Blue Alliance (TBA) API integration.

This test file validates:
- Multi-event synchronization
- Event filtering
- Match data retrieval with alliance information
"""
import pytest
from unittest.mock import Mock, patch
import json


@pytest.mark.django_db
class TestComplexTBAIntegration:
    """Complex integration tests for The Blue Alliance API integration."""

    @patch('tba.util.requests.get')
    def test_sync_season_with_multiple_events_and_matches(self, mock_get):
        """Test synchronizing a complete season with multiple events and their matches."""
        from tba.util import get_events_for_team
        from scouting.models import Season, Team
        
        # Setup: Create season and team
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        
        team = Team.objects.create(
            team_no=3492,
            team_nm='PARTs',
            void_ind='n'
        )
        
        # Mock TBA API responses
        mock_events_response = Mock()
        mock_events_response.text = json.dumps([
            {
                'key': '2024week1',
                'name': 'Week 1 Event',
                'event_type': 0,
                'start_date': '2024-03-01',
                'end_date': '2024-03-03'
            },
            {
                'key': '2024week2',
                'name': 'Week 2 Event',
                'event_type': 0,
                'start_date': '2024-03-08',
                'end_date': '2024-03-10'
            }
        ])
        
        mock_get.return_value = mock_events_response
        
        # Test: Get events for team
        with patch('tba.util.get_tba_event') as mock_get_event:
            mock_get_event.side_effect = [
                {
                    'event_cd': '2024week1',
                    'event_nm': 'Week 1 Event',
                    'date_st': '2024-03-01',
                    'date_end': '2024-03-03'
                },
                {
                    'event_cd': '2024week2',
                    'event_nm': 'Week 2 Event',
                    'date_st': '2024-03-08',
                    'date_end': '2024-03-10'
                }
            ]
            
            events = get_events_for_team(team, season)
            
            # Verify API was called
            assert mock_get.called
            # Verify events were retrieved
            assert len(events) == 2
            assert events[0]['event_cd'] == '2024week1'
            assert events[1]['event_cd'] == '2024week2'

    @patch('tba.util.requests.get')
    def test_get_events_with_filtering(self, mock_get):
        """Test getting events for a team with specific events filtered out."""
        from tba.util import get_events_for_team
        from scouting.models import Season, Team
        
        # Setup
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        team = Team.objects.create(
            team_no=3492,
            team_nm='PARTs',
            void_ind='n'
        )
        
        # Mock response with multiple events
        mock_response = Mock()
        mock_response.text = json.dumps([
            {'key': '2024event1', 'name': 'Event 1'},
            {'key': '2024event2', 'name': 'Event 2'},
            {'key': '2024event3', 'name': 'Event 3'}
        ])
        mock_get.return_value = mock_response
        
        # Test: Get events but ignore event2
        with patch('tba.util.get_tba_event') as mock_get_event:
            mock_get_event.side_effect = [
                {'event_cd': '2024event1', 'event_nm': 'Event 1'},
                {'event_cd': '2024event3', 'event_nm': 'Event 3'}
            ]
            
            events = get_events_for_team(team, season, event_cds_to_ignore=['2024event2'])
            
            # Should return 3 events, but event2 should have minimal data
            assert len(events) == 3
            assert events[0]['event_cd'] == '2024event1'
            assert events[1] == {'event_cd': '2024event2'}  # Ignored event
            assert events[2]['event_cd'] == '2024event3'

    @patch('tba.util.requests.get')
    def test_match_retrieval_with_alliance_data(self, mock_get):
        """Test retrieving match data with complete alliance information."""
        from tba.util import get_matches_for_team_event
        
        # Mock match data with alliances
        mock_response = Mock()
        mock_response.text = json.dumps([
            {
                'key': '2024event1_qm1',
                'match_number': 1,
                'alliances': {
                    'red': {
                        'team_keys': ['frc3492', 'frc1234', 'frc5678'],
                        'score': 150
                    },
                    'blue': {
                        'team_keys': ['frc1111', 'frc2222', 'frc3333'],
                        'score': 145
                    }
                },
                'winning_alliance': 'red'
            },
            {
                'key': '2024event1_qm2',
                'match_number': 2,
                'alliances': {
                    'red': {
                        'team_keys': ['frc1111', 'frc2222', 'frc3333'],
                        'score': 160
                    },
                    'blue': {
                        'team_keys': ['frc3492', 'frc1234', 'frc5678'],
                        'score': 155
                    }
                },
                'winning_alliance': 'red'
            }
        ])
        mock_get.return_value = mock_response
        
        # Test
        matches = get_matches_for_team_event('3492', '2024event1')
        
        # Verify
        assert len(matches) == 2
        assert matches[0]['match_number'] == 1
        assert 'frc3492' in matches[0]['alliances']['red']['team_keys']
        assert matches[1]['match_number'] == 2
        assert 'frc3492' in matches[1]['alliances']['blue']['team_keys']
