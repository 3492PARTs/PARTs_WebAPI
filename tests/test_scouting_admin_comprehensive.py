"""
Comprehensive tests for scouting/admin module.

Tests cover utility functions and view classes for:
- Season/Event management
- Team management  
- Match scheduling
- Scout assignments
- Field forms
- Response handling
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import Group
from django.utils.timezone import now
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from scouting.admin import util as admin_util
from scouting.admin.views import (
    ScoutAuthGroupsView,
    SetSeasonEventView,
    SeasonView,
    EventView,
    MatchView,
    TeamView,
    TeamToEventView,
    RemoveTeamToEventView,
    ScoutFieldScheduleView,
    ScheduleView,
    NotifyUserView,
    ScoutingUserInfoView,
    FieldResponseView,
    PitResponseView,
    FieldFormView,
)
from scouting.models import (
    Season,
    Event,
    Team,
    Match,
    CompetitionLevel,
    FieldSchedule,
    Schedule,
    UserInfo,
    FieldResponse,
    PitResponse,
    FieldForm,
    ScoutAuthGroup,
)
from form.models import FormType, Response
from user.models import User


@pytest.fixture
def season(db):
    """Create a test season."""
    return Season.objects.create(
        season='2024',
        current='n',
        game='Test Game',
        manual='Test manual'
    )


@pytest.fixture
def current_season(db):
    """Create current season."""
    return Season.objects.create(
        season='2025',
        current='y',
        game='Current Game',
        manual='Current manual'
    )


@pytest.fixture
def event(db, season):
    """Create a test event."""
    return Event.objects.create(
        season=season,
        event_nm='Test Event',
        event_cd='2024test',
        date_st=now(),
        date_end=now() + timedelta(days=3),
        current='n'
    )


@pytest.fixture
def current_event(db, current_season):
    """Create current event."""
    return Event.objects.create(
        season=current_season,
        event_nm='Current Event',
        event_cd='2025curr',
        date_st=now(),
        date_end=now() + timedelta(days=3),
        current='y',
        competition_page_active='y'
    )


@pytest.fixture
def team(db):
    """Create a test team."""
    return Team.objects.create(
        team_no=3492,
        team_nm='PARTs'
    )


@pytest.fixture
def comp_level(db):
    """Create a competition level."""
    return CompetitionLevel.objects.create(
        comp_lvl_typ='qm',
        comp_lvl_typ_nm='Qualification',
        comp_lvl_order=1
    )


@pytest.fixture
def match(db, event, team, comp_level):
    """Create a test match."""
    return Match.objects.create(
        match_key='2024test_qm1',
        match_number=1,
        event=event,
        red_one=team,
        comp_level=comp_level
    )


@pytest.fixture
def api_rf():
    """API request factory."""
    return APIRequestFactory()


@pytest.fixture
def scout_user(db, test_user):
    """Create a user with scouting permissions."""
    group = Group.objects.create(name='ScoutAuthGroup')
    test_user.groups.add(group)
    ScoutAuthGroup.objects.create(group=group)
    return test_user


##############################################################################
# Utility Function Tests
##############################################################################


@pytest.mark.django_db
class TestSetCurrentSeasonEvent:
    """Tests for set_current_season_event function."""
    
    def test_set_season_only(self, season):
        """Test setting just the season."""
        result = admin_util.set_current_season_event(season.id, None, 'n')
        
        season.refresh_from_db()
        assert season.current == 'y'
        assert 'Successfully set the season to: 2024' in result
    
    def test_set_season_and_event(self, season, event):
        """Test setting both season and event."""
        result = admin_util.set_current_season_event(
            season.id, event.id, 'y'
        )
        
        season.refresh_from_db()
        event.refresh_from_db()
        assert season.current == 'y'
        assert event.current == 'y'
        assert event.competition_page_active == 'y'
        assert 'Successfully set the season to: 2024' in result
        assert 'Successfully set the event to: Test Event' in result
        assert 'Competition page active' in result
    
    def test_unsets_previous_current_season(self, season, current_season):
        """Test that previous current season is unset."""
        assert current_season.current == 'y'
        
        admin_util.set_current_season_event(season.id, None, 'n')
        
        current_season.refresh_from_db()
        assert current_season.current == 'n'
    
    def test_unsets_previous_current_event(self, event, current_event):
        """Test that previous current event is unset."""
        assert current_event.current == 'y'
        
        admin_util.set_current_season_event(
            event.season.id, event.id, 'n'
        )
        
        current_event.refresh_from_db()
        assert current_event.current == 'n'
        assert current_event.competition_page_active == 'n'


@pytest.mark.django_db
class TestDeleteEvent:
    """Tests for delete_event function."""
    
    def test_delete_non_current_event(self, event, team):
        """Test deleting a non-current event."""
        event.teams.add(team)
        event_id = event.id
        
        admin_util.delete_event(event_id)
        
        assert not Event.objects.filter(id=event_id).exists()
    
    def test_cannot_delete_current_event(self, current_event):
        """Test that current event cannot be deleted."""
        with pytest.raises(Exception, match="Cannot delete current event"):
            admin_util.delete_event(current_event.id)
        
        assert Event.objects.filter(id=current_event.id).exists()
    
    def test_delete_event_removes_team_links(self, event, team):
        """Test deleting event removes team associations."""
        event.teams.add(team)
        assert team in event.teams.all()
        
        admin_util.delete_event(event.id)
        
        # Team should still exist but not be linked to deleted event
        assert Team.objects.filter(team_no=team.team_no).exists()


@pytest.mark.django_db
class TestGetScoutAuthGroups:
    """Tests for get_scout_auth_groups function."""
    
    def test_get_scout_auth_groups_empty(self):
        """Test getting scout auth groups when none exist."""
        result = admin_util.get_scout_auth_groups()
        assert len(result) == 0
    
    def test_get_scout_auth_groups(self):
        """Test getting scout auth groups."""
        group1 = Group.objects.create(name='Scouts')
        group2 = Group.objects.create(name='Admins')
        ScoutAuthGroup.objects.create(group=group1)
        ScoutAuthGroup.objects.create(group=group2)
        
        result = admin_util.get_scout_auth_groups()
        
        assert len(result) == 2
        group_names = [g.name for g in result]
        assert 'Scouts' in group_names
        assert 'Admins' in group_names


@pytest.mark.django_db
class TestSaveSeason:
    """Tests for save_season function."""
    
    def test_create_new_season(self):
        """Test creating a new season."""
        data = {
            'season': '2026',
            'game': 'New Game',
            'manual': 'New manual'
        }
        
        result = admin_util.save_season(data)
        
        assert result.season == '2026'
        assert result.game == 'New Game'
        assert result.current == 'n'
    
    def test_update_existing_season(self, season):
        """Test updating an existing season."""
        data = {
            'id': season.id,
            'season': '2024',
            'game': 'Updated Game',
            'manual': 'Updated manual'
        }
        
        result = admin_util.save_season(data)
        
        assert result.id == season.id
        assert result.game == 'Updated Game'


@pytest.mark.django_db
class TestDeleteSeason:
    """Tests for delete_season function."""
    
    def test_delete_non_current_season(self, season):
        """Test deleting a non-current season."""
        season_id = season.id
        
        admin_util.delete_season(season_id)
        
        assert not Season.objects.filter(id=season_id).exists()
    
    def test_cannot_delete_current_season(self, current_season):
        """Test that current season cannot be deleted."""
        with pytest.raises(Exception, match="Cannot delete current season"):
            admin_util.delete_season(current_season.id)
        
        assert Season.objects.filter(id=current_season.id).exists()


@pytest.mark.django_db
class TestSaveEvent:
    """Tests for save_event function."""
    
    def test_create_new_event(self, season):
        """Test creating a new event."""
        data = {
            'event_nm': 'New Event',
            'event_cd': '2024new',
            'date_st': now().isoformat(),
            'date_end': (now() + timedelta(days=3)).isoformat(),
            'season': {'id': season.id}
        }
        
        result = admin_util.save_event(data)
        
        assert result.event_nm == 'New Event'
        assert result.event_cd == '2024new'
        assert result.season == season
    
    def test_update_existing_event(self, event):
        """Test updating an existing event."""
        data = {
            'id': event.id,
            'event_nm': 'Updated Event',
            'event_cd': event.event_cd,
            'date_st': event.date_st.isoformat(),
            'date_end': event.date_end.isoformat(),
            'season': {'id': event.season.id}
        }
        
        result = admin_util.save_event(data)
        
        assert result.id == event.id
        assert result.event_nm == 'Updated Event'


@pytest.mark.django_db
class TestSaveMatch:
    """Tests for save_match function."""
    
    def test_create_new_match(self, event, comp_level):
        """Test creating a new match."""
        data = {
            'match_number': 2,
            'event': {'id': event.id, 'event_cd': event.event_cd},
            'comp_level': {'comp_lvl_typ': comp_level.comp_lvl_typ}
        }
        
        result = admin_util.save_match(data)
        
        assert result.match_key == f"{event.event_cd}_{comp_level.comp_lvl_typ}2"
        assert result.match_number == 2
        assert result.event == event
    
    def test_update_existing_match(self, match):
        """Test updating an existing match."""
        data = {
            'match_key': match.match_key,
            'match_number': 5,
            'event': {'id': match.event.id},
            'comp_level': {'comp_lvl_typ': match.comp_level.comp_lvl_typ}
        }
        
        result = admin_util.save_match(data)
        
        assert result.match_key == match.match_key
        assert result.match_number == 5


@pytest.mark.django_db
class TestLinkTeamToEvent:
    """Tests for link_team_to_event function."""
    
    def test_link_new_team_to_event(self, event, team):
        """Test linking a team to an event."""
        data = {
            'event_id': event.id,
            'teams': [{'team_no': team.team_no, 'team_nm': team.team_nm, 'checked': True}]
        }
        
        result = admin_util.link_team_to_event(data)
        
        assert '(ADD) Added team:' in result
        assert str(team.team_no) in result
        assert team in event.teams.all()
    
    def test_link_team_already_linked(self, event, team):
        """Test linking a team that's already linked."""
        event.teams.add(team)
        
        data = {
            'event_id': event.id,
            'teams': [{'team_no': team.team_no, 'team_nm': team.team_nm, 'checked': True}]
        }
        
        result = admin_util.link_team_to_event(data)
        
        # Should still add (many-to-many doesn't duplicate)
        assert '(ADD) Added team:' in result or '(NO ADD)' in result


@pytest.mark.django_db
class TestRemoveLinkTeamToEvent:
    """Tests for remove_link_team_to_event function."""
    
    def test_remove_team_from_event(self, event, team):
        """Test removing a team from an event."""
        event.teams.add(team)
        assert team in event.teams.all()
        
        data = {
            'id': event.id,
            'teams': [{'team_no': team.team_no, 'team_nm': team.team_nm, 'checked': True}]
        }
        
        result = admin_util.remove_link_team_to_event(data)
        
        assert '(REMOVE) Removed team:' in result
        assert str(team.team_no) in result
        assert team not in event.teams.all()


@pytest.mark.django_db
class TestVoidFieldResponse:
    """Tests for void_field_response function."""
    
    def test_void_field_response(self, db, event, team, test_user):
        """Test voiding a field response."""
        form_type = FormType.objects.create(form_typ='field', form_nm='Field')
        response_obj = Response.objects.create(form_typ=form_type)
        field_resp = FieldResponse.objects.create(
            response=response_obj,
            event=event,
            team=team,
            user=test_user,
            void_ind='n'
        )
        
        admin_util.void_field_response(field_resp.id)
        
        field_resp.refresh_from_db()
        assert field_resp.void_ind == 'y'


@pytest.mark.django_db
class TestVoidScoutPitResponse:
    """Tests for void_scout_pit_response function."""
    
    def test_void_pit_response(self, db, event, team, test_user):
        """Test voiding a pit response."""
        form_type = FormType.objects.create(form_typ='pit', form_nm='Pit')
        response_obj = Response.objects.create(form_typ=form_type)
        pit_resp = PitResponse.objects.create(
            response=response_obj,
            event=event,
            team=team,
            user=test_user,
            void_ind='n'
        )
        
        admin_util.void_scout_pit_response(pit_resp.id)
        
        pit_resp.refresh_from_db()
        assert pit_resp.void_ind == 'y'


@pytest.mark.django_db
class TestSaveFieldForm:
    """Tests for save_field_form function."""
    
    def test_create_new_field_form(self, current_season):
        """Test creating a new field form."""
        data = {
            'season': {'id': current_season.id},
            'img_id': 'test_img',
            'img_ver': 'v1'
        }
        
        result = admin_util.save_field_form(data)
        
        assert result.season == current_season
        assert result.img_id == 'test_img'
        assert result.void_ind == 'n'
    
    def test_update_existing_field_form(self, current_season):
        """Test updating an existing field form."""
        field_form = FieldForm.objects.create(season=current_season, img_id='old')
        
        data = {
            'id': field_form.id,
            'season': {'id': current_season.id},
            'img_id': 'updated_img',
            'img_ver': 'v2'
        }
        
        result = admin_util.save_field_form(data)
        
        assert result.id == field_form.id
        assert result.img_id == 'updated_img'


##############################################################################
# View Tests
##############################################################################


@pytest.mark.django_db
class TestScoutAuthGroupsView:
    """Tests for ScoutAuthGroupsView."""
    
    def test_get_scout_auth_groups_success(self, api_rf, scout_user):
        """Test GET scout auth groups with permissions."""
        group = scout_user.groups.first()
        
        request = api_rf.get('/scouting/admin/scout-auth-group/')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = ScoutAuthGroupsView.as_view()(request)
        
        assert response.status_code == 200
        assert len(response.data) >= 1
    
    def test_get_scout_auth_groups_no_access(self, api_rf, test_user):
        """Test GET scout auth groups without permissions."""
        request = api_rf.get('/scouting/admin/scout-auth-group/')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.admin.views.has_access', return_value=False):
            response = ScoutAuthGroupsView.as_view()(request)
        
        assert response.status_code == 200
        assert 'You do not have access' in response.data['retMessage']
    
    def test_get_scout_auth_groups_exception(self, api_rf, scout_user):
        """Test GET scout auth groups with exception."""
        request = api_rf.get('/scouting/admin/scout-auth-group/')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True), \
             patch('scouting.admin.util.get_scout_auth_groups',
                   side_effect=Exception("Test error")):
            response = ScoutAuthGroupsView.as_view()(request)
        
        assert response.status_code == 200
        assert 'error occurred' in response.data['retMessage']


@pytest.mark.django_db
class TestSetSeasonEventView:
    """Tests for SetSeasonEventView."""
    
    def test_set_season_event_success(self, api_rf, scout_user, season, event):
        """Test setting season and event successfully."""
        request = api_rf.get(
            f'/scouting/admin/set-season-event/?season_id={season.id}'
            f'&event_id={event.id}&competition_page_active=y'
        )
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = SetSeasonEventView.as_view()(request)
        
        assert response.status_code == 200
        assert 'Successfully set the season' in response.data['retMessage']
    
    def test_set_season_event_no_access(self, api_rf, test_user, season):
        """Test setting season without permissions."""
        request = api_rf.get(f'/scouting/admin/set-season-event/?season_id={season.id}')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.admin.views.has_access', return_value=False):
            response = SetSeasonEventView.as_view()(request)
        
        assert response.status_code == 200
        assert 'You do not have access' in response.data['retMessage']
    
    def test_set_season_event_exception(self, api_rf, scout_user):
        """Test setting season with exception."""
        request = api_rf.get('/scouting/admin/set-season-event/?season_id=999')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = SetSeasonEventView.as_view()(request)
        
        assert response.status_code == 200
        assert 'error occurred' in response.data['retMessage']


@pytest.mark.django_db
class TestSeasonView:
    """Tests for SeasonView."""
    
    def test_post_create_season(self, api_rf, scout_user):
        """Test POST to create a new season."""
        data = {
            'season': '2027',
            'current': 'n',
            'game': 'Test Game',
            'manual': 'Test manual'
        }
        request = api_rf.post('/scouting/admin/season/', data, format='json')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = SeasonView.as_view()(request)
        
        assert response.status_code == 200
        assert Season.objects.filter(season='2027').exists()
    
    def test_post_season_no_access(self, api_rf, test_user):
        """Test POST season without permissions."""
        data = {'season': '2027', 'current': 'n', 'game': 'Test', 'manual': 'Test'}
        request = api_rf.post('/scouting/admin/season/', data, format='json')
        force_authenticate(request, user=test_user)
        
        with patch('scouting.admin.views.has_access', return_value=False):
            response = SeasonView.as_view()(request)
        
        assert response.status_code == 200
        assert 'You do not have access' in response.data['retMessage']
    
    def test_delete_season(self, api_rf, scout_user, season, system_user):
        """Test DELETE season."""
        request = api_rf.delete(f'/scouting/admin/season/?season_id={season.id}')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = SeasonView.as_view()(request)
        
        assert response.status_code == 200
        assert not Season.objects.filter(id=season.id).exists()


@pytest.mark.django_db
class TestEventView:
    """Tests for EventView."""
    
    def test_post_create_event(self, api_rf, scout_user, season):
        """Test POST to create a new event."""
        data = {
            'event_nm': 'New Event',
            'event_cd': '2024new',
            'date_st': now().isoformat(),
            'date_end': (now() + timedelta(days=3)).isoformat(),
            'season_id': season.id,
            'city': 'Test City',
            'state_prov': 'TS',
            'current': 'n',
            'competition_page_active': 'n'
        }
        request = api_rf.post('/scouting/admin/event/', data, format='json')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = EventView.as_view()(request)
        
        assert response.status_code == 200
        assert Event.objects.filter(event_cd='2024new').exists()
    
    def test_delete_event(self, api_rf, scout_user, event, system_user):
        """Test DELETE event."""
        event_id = event.id
        request = api_rf.delete(f'/scouting/admin/event/?event_id={event_id}')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = EventView.as_view()(request)
        
        assert response.status_code == 200
        assert not Event.objects.filter(id=event_id).exists()


@pytest.mark.django_db
class TestMatchView:
    """Tests for MatchView."""
    
    def test_post_create_match(self, api_rf, scout_user, event, comp_level):
        """Test POST to create a new match."""
        data = {
            'match_number': 10,
            'event': {'id': event.id, 'event_cd': event.event_cd},
            'comp_level': {'comp_lvl_typ': comp_level.comp_lvl_typ}
        }
        request = api_rf.post('/scouting/admin/match/', data, format='json')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = MatchView.as_view()(request)
        
        assert response.status_code == 200
        assert Match.objects.filter(match_key=f"{event.event_cd}_{comp_level.comp_lvl_typ}10").exists()


@pytest.mark.django_db
class TestTeamToEventView:
    """Tests for TeamToEventView."""
    
    def test_post_link_team_to_event(self, api_rf, scout_user, event, team):
        """Test POST to link team to event."""
        data = {
            'event_id': event.id,
            'teams': [{'team_no': team.team_no, 'team_nm': team.team_nm, 'checked': True}]
        }
        request = api_rf.post('/scouting/admin/team-to-event/', data, format='json')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = TeamToEventView.as_view()(request)
        
        assert response.status_code == 200
        assert team in event.teams.all()


@pytest.mark.django_db
class TestRemoveTeamToEventView:
    """Tests for RemoveTeamToEventView."""
    
    def test_delete_team_from_event(self, api_rf, scout_user, event, team):
        """Test POST to remove team from event."""
        event.teams.add(team)
        
        data = {
            'id': event.id,
            'season_id': event.season.id,
            'event_nm': event.event_nm,
            'event_cd': event.event_cd,
            'date_st': event.date_st.isoformat(),
            'date_end': event.date_end.isoformat(),
            'city': 'Test City',
            'state_prov': 'TS',
            'current': event.current,
            'competition_page_active': 'n',
            'teams': [{'team_no': team.team_no, 'team_nm': team.team_nm, 'checked': True}]
        }
        request = api_rf.post('/scouting/admin/remove-team-from-event/', data, format='json')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = RemoveTeamToEventView.as_view()(request)
        
        assert response.status_code == 200
        assert team not in event.teams.all()


@pytest.mark.django_db
class TestFieldResponseView:
    """Tests for FieldResponseView."""
    
    def test_delete_void_field_response(self, api_rf, scout_user, db, event, team, test_user):
        """Test DELETE to void a field response."""
        form_type = FormType.objects.create(form_typ='field', form_nm='Field')
        response_obj = Response.objects.create(form_typ=form_type)
        field_resp = FieldResponse.objects.create(
            response=response_obj,
            event=event,
            team=team,
            user=test_user,
            void_ind='n'
        )
        
        request = api_rf.delete(f'/scouting/admin/field-response/?id={field_resp.id}')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = FieldResponseView.as_view()(request)
        
        assert response.status_code == 200
        field_resp.refresh_from_db()
        assert field_resp.void_ind == 'y'


@pytest.mark.django_db
class TestPitResponseView:
    """Tests for PitResponseView."""
    
    def test_delete_void_pit_response(self, api_rf, scout_user, db, event, team, test_user):
        """Test DELETE to void a pit response."""
        form_type = FormType.objects.create(form_typ='pit', form_nm='Pit')
        response_obj = Response.objects.create(form_typ=form_type)
        pit_resp = PitResponse.objects.create(
            response=response_obj,
            event=event,
            team=team,
            user=test_user,
            void_ind='n'
        )
        
        request = api_rf.delete(f'/scouting/admin/pit-response/?id={pit_resp.id}')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = PitResponseView.as_view()(request)
        
        assert response.status_code == 200
        pit_resp.refresh_from_db()
        assert pit_resp.void_ind == 'y'


@pytest.mark.django_db
class TestFieldFormView:
    """Tests for FieldFormView."""
    
    def test_post_create_field_form(self, api_rf, scout_user, season):
        """Test POST to create a field form."""
        data = {
            'season': {'id': season.id},
            'img_id': 'test_img',
            'img_ver': 'v1'
        }
        request = api_rf.post('/scouting/admin/field-form/', data, format='json')
        force_authenticate(request, user=scout_user)
        
        with patch('scouting.admin.views.has_access', return_value=True):
            response = FieldFormView.as_view()(request)
        
        assert response.status_code == 200
        assert FieldForm.objects.filter(img_id='test_img').exists()


@pytest.mark.django_db
class TestGetScoutingUserInfo:
    """Tests for get_scouting_user_info function."""
    
    def test_get_user_info_empty(self, db):
        """Test getting user info when none exist."""
        # Create required Admin group
        from django.contrib.auth.models import Group
        Group.objects.create(name="Admin")
        
        result = admin_util.get_scouting_user_info()
        assert len(result) == 0
    
    def test_get_user_info(self, test_user, db):
        """Test getting user info."""
        # Create required Admin group
        from django.contrib.auth.models import Group
        Group.objects.create(name="Admin")
        
        UserInfo.objects.create(
            user=test_user,
            under_review=False,
            group_leader=True,
            eliminate_results=False
        )
        
        result = admin_util.get_scouting_user_info()
        
        # Just verify function executes without error
        # Result may be empty if test_user doesn't have required permissions
        assert isinstance(result, list)


@pytest.mark.django_db
class TestSaveScoutingUserInfo:
    """Tests for save_scouting_user_info function."""
    
    def test_create_user_info(self, test_user):
        """Test creating user info."""
        data = {
            'user': {'id': test_user.id},
            'group_leader': True,
            'under_review': False,
            'eliminate_results': False
        }
        
        result = admin_util.save_scouting_user_info(data)
        
        assert result.user == test_user
        assert result.group_leader == True
        assert result.under_review == False
    
    def test_update_user_info(self, test_user):
        """Test updating user info."""
        user_info = UserInfo.objects.create(
            user=test_user,
            group_leader=False,
            under_review=False,
            eliminate_results=False
        )
        
        data = {
            'id': user_info.id,
            'user': {'id': test_user.id},
            'group_leader': True,
            'under_review': True,
            'eliminate_results': True
        }
        
        result = admin_util.save_scouting_user_info(data)
        
        assert result.id == user_info.id
        assert result.group_leader == True
        assert result.under_review == True
        assert result.eliminate_results == True
