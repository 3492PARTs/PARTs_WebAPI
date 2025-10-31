"""
Comprehensive tests for scouting/portal module.

This module tests the serializers in scouting/portal which are used
for composing schedule and field schedule data for the portal interface.
"""

import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from scouting.portal.serializers import (
    ScheduleByTypeSerializer,
    InitSerializer,
)
from scouting.models import (
    Season,
    Event,
    Schedule,
    ScheduleType,
    FieldSchedule,
    Match,
    CompetitionLevel,
)
from user.models import User


@pytest.fixture
def season(db):
    """Create a test season."""
    return Season.objects.create(
        season=2024,
        current='y'
    )


@pytest.fixture
def event(db, season):
    """Create a test event."""
    return Event.objects.create(
        season=season,
        event_nm='Test Event',
        date_st=timezone.now().date(),
        date_end=(timezone.now() + timedelta(days=3)).date(),
        current='y',
        void_ind='n'
    )


@pytest.fixture
def schedule_type(db):
    """Create a test schedule type."""
    return ScheduleType.objects.create(
        sch_typ='meeting',
        sch_nm='Meeting'
    )


@pytest.fixture
def schedule(db, event, schedule_type):
    """Create a test schedule."""
    return Schedule.objects.create(
        event=event,
        sch_typ=schedule_type,
        sch_nm='Team Meeting',
        st_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=2),
        void_ind='n'
    )


@pytest.fixture
def test_user(db):
    """Create a test user."""
    return User.objects.create(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def competition_level(db):
    """Create a competition level."""
    return CompetitionLevel.objects.create(
        comp_lvl='qm',
        comp_lvl_order=1
    )


@pytest.fixture
def match(db, event, competition_level):
    """Create a test match."""
    return Match.objects.create(
        event=event,
        match_number=1,
        comp_level=competition_level,
        void_ind='n'
    )


@pytest.fixture
def field_schedule(db, match, test_user):
    """Create a test field schedule."""
    return FieldSchedule.objects.create(
        match=match,
        st_time=timezone.now(),
        end_time=timezone.now() + timedelta(hours=1),
        red_one=test_user,
        notification1=True,
        notification2=False,
        void_ind='n'
    )


@pytest.mark.django_db
class TestScheduleByTypeSerializer:
    """Test ScheduleByTypeSerializer."""
    
    def test_serialize_with_schedule_type_and_schedules(self, schedule_type, schedule):
        """Test serialization with schedule type and multiple schedules."""
        data = {
            'sch_typ': schedule_type,
            'sch': [schedule]
        }
        
        serializer = ScheduleByTypeSerializer(data)
        result = serializer.data
        
        assert 'sch_typ' in result
        assert result['sch_typ']['sch_typ'] == 'meeting'
        assert result['sch_typ']['sch_nm'] == 'Meeting'
        assert 'sch' in result
        assert len(result['sch']) == 1
        assert result['sch'][0]['sch_nm'] == 'Team Meeting'
    
    def test_serialize_with_schedule_type_only(self, schedule_type):
        """Test serialization with only schedule type, no schedules."""
        data = {
            'sch_typ': schedule_type,
        }
        
        serializer = ScheduleByTypeSerializer(data)
        result = serializer.data
        
        assert 'sch_typ' in result
        assert result['sch_typ']['sch_typ'] == 'meeting'
        # sch field should not be present or be empty
        assert 'sch' not in result or result['sch'] is None
    
    def test_serialize_multiple_schedules(self, schedule_type, event):
        """Test serialization with multiple schedules of same type."""
        schedule1 = Schedule.objects.create(
            event=event,
            sch_typ=schedule_type,
            sch_nm='Morning Meeting',
            st_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
            void_ind='n'
        )
        schedule2 = Schedule.objects.create(
            event=event,
            sch_typ=schedule_type,
            sch_nm='Afternoon Meeting',
            st_time=timezone.now() + timedelta(hours=5),
            end_time=timezone.now() + timedelta(hours=6),
            void_ind='n'
        )
        
        data = {
            'sch_typ': schedule_type,
            'sch': [schedule1, schedule2]
        }
        
        serializer = ScheduleByTypeSerializer(data)
        result = serializer.data
        
        assert len(result['sch']) == 2
        schedule_names = [s['sch_nm'] for s in result['sch']]
        assert 'Morning Meeting' in schedule_names
        assert 'Afternoon Meeting' in schedule_names


@pytest.mark.django_db
class TestInitSerializer:
    """Test InitSerializer for portal initialization."""
    
    def test_serialize_empty_data(self):
        """Test serialization with empty/minimal data."""
        data = {}
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        # All fields are optional, so empty dict should serialize
        assert isinstance(result, dict)
    
    def test_serialize_with_field_schedule(self, field_schedule):
        """Test serialization with field schedule data."""
        data = {
            'fieldSchedule': [field_schedule]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert 'fieldSchedule' in result
        assert len(result['fieldSchedule']) == 1
        assert result['fieldSchedule'][0]['notification1'] is True
        assert result['fieldSchedule'][0]['notification2'] is False
    
    def test_serialize_with_schedule(self, schedule):
        """Test serialization with regular schedule data."""
        data = {
            'schedule': [schedule]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert 'schedule' in result
        assert len(result['schedule']) == 1
        assert result['schedule'][0]['sch_nm'] == 'Team Meeting'
    
    def test_serialize_with_all_field_schedule(self, field_schedule):
        """Test serialization with allFieldSchedule data."""
        data = {
            'allFieldSchedule': [field_schedule]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert 'allFieldSchedule' in result
        assert len(result['allFieldSchedule']) == 1
    
    def test_serialize_with_all_schedule_by_type(self, schedule_type, schedule):
        """Test serialization with allSchedule data grouped by type."""
        schedule_by_type_data = {
            'sch_typ': schedule_type,
            'sch': [schedule]
        }
        
        data = {
            'allSchedule': [schedule_by_type_data]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert 'allSchedule' in result
        assert len(result['allSchedule']) == 1
        assert result['allSchedule'][0]['sch_typ']['sch_typ'] == 'meeting'
        assert len(result['allSchedule'][0]['sch']) == 1
    
    def test_serialize_with_users(self, test_user):
        """Test serialization with user data."""
        data = {
            'users': [test_user]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert 'users' in result
        assert len(result['users']) == 1
        assert result['users'][0]['username'] == 'testuser'
        assert result['users'][0]['email'] == 'test@example.com'
    
    def test_serialize_with_schedule_types(self, schedule_type):
        """Test serialization with schedule type data."""
        data = {
            'scheduleTypes': [schedule_type]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert 'scheduleTypes' in result
        assert len(result['scheduleTypes']) == 1
        assert result['scheduleTypes'][0]['sch_typ'] == 'meeting'
        assert result['scheduleTypes'][0]['sch_nm'] == 'Meeting'
    
    def test_serialize_complete_init_data(
        self, field_schedule, schedule, schedule_type, test_user
    ):
        """Test serialization with all fields populated."""
        schedule_by_type_data = {
            'sch_typ': schedule_type,
            'sch': [schedule]
        }
        
        data = {
            'fieldSchedule': [field_schedule],
            'schedule': [schedule],
            'allFieldSchedule': [field_schedule],
            'allSchedule': [schedule_by_type_data],
            'users': [test_user],
            'scheduleTypes': [schedule_type]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        # Verify all fields are present
        assert 'fieldSchedule' in result
        assert 'schedule' in result
        assert 'allFieldSchedule' in result
        assert 'allSchedule' in result
        assert 'users' in result
        assert 'scheduleTypes' in result
        
        # Verify data integrity
        assert len(result['fieldSchedule']) == 1
        assert len(result['schedule']) == 1
        assert len(result['allFieldSchedule']) == 1
        assert len(result['allSchedule']) == 1
        assert len(result['users']) == 1
        assert len(result['scheduleTypes']) == 1
    
    def test_serialize_multiple_users(self, test_user):
        """Test serialization with multiple users."""
        user2 = User.objects.create(
            username='testuser2',
            email='test2@example.com',
            first_name='Test2',
            last_name='User2'
        )
        
        data = {
            'users': [test_user, user2]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert len(result['users']) == 2
        usernames = [u['username'] for u in result['users']]
        assert 'testuser' in usernames
        assert 'testuser2' in usernames
    
    def test_serialize_multiple_schedule_types(self):
        """Test serialization with multiple schedule types."""
        type1 = ScheduleType.objects.create(sch_typ='meeting', sch_nm='Meeting')
        type2 = ScheduleType.objects.create(sch_typ='practice', sch_nm='Practice')
        
        data = {
            'scheduleTypes': [type1, type2]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert len(result['scheduleTypes']) == 2
        type_codes = [t['sch_typ'] for t in result['scheduleTypes']]
        assert 'meeting' in type_codes
        assert 'practice' in type_codes


@pytest.mark.django_db
class TestPortalModuleConstants:
    """Test portal module configuration constants."""
    
    def test_portal_auth_object(self):
        """Test that portal auth object is defined."""
        from scouting.portal import views as portal_views
        
        assert hasattr(portal_views, 'auth_obj')
        assert portal_views.auth_obj == "scoutPortal"
    
    def test_portal_scheduling_auth_object(self):
        """Test that scheduling auth object is defined."""
        from scouting.portal import views as portal_views
        
        assert hasattr(portal_views, 'scheduling_auth_obj')
        assert portal_views.scheduling_auth_obj == "scheduling"
    
    def test_portal_app_url(self):
        """Test that portal app URL is defined."""
        from scouting.portal import views as portal_views
        
        assert hasattr(portal_views, 'app_url')
        assert portal_views.app_url == "scouting/portal/"


@pytest.mark.django_db
class TestPortalSerializerEdgeCases:
    """Test edge cases and validation for portal serializers."""
    
    def test_schedule_by_type_with_empty_schedule_list(self, schedule_type):
        """Test ScheduleByTypeSerializer with empty schedule list."""
        data = {
            'sch_typ': schedule_type,
            'sch': []
        }
        
        serializer = ScheduleByTypeSerializer(data)
        result = serializer.data
        
        assert 'sch_typ' in result
        assert 'sch' in result
        assert result['sch'] == []
    
    def test_init_serializer_partial_data(self, field_schedule):
        """Test InitSerializer with only some fields populated."""
        data = {
            'fieldSchedule': [field_schedule],
            # Other fields intentionally omitted
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert 'fieldSchedule' in result
        assert len(result['fieldSchedule']) == 1
        # Other fields should not be present or be None
        for field in ['schedule', 'allFieldSchedule', 'allSchedule', 'users', 'scheduleTypes']:
            if field in result:
                assert result[field] is None or result[field] == []
    
    def test_init_serializer_with_mixed_data_types(
        self, field_schedule, schedule, schedule_type, test_user
    ):
        """Test InitSerializer handles different data combinations."""
        # Create different schedule type
        type2 = ScheduleType.objects.create(sch_typ='competition', sch_nm='Competition')
        
        schedule_by_type1 = {
            'sch_typ': schedule_type,
            'sch': [schedule]
        }
        schedule_by_type2 = {
            'sch_typ': type2,
            'sch': []  # Empty schedule list
        }
        
        data = {
            'allSchedule': [schedule_by_type1, schedule_by_type2],
            'users': [test_user]
        }
        
        serializer = InitSerializer(data)
        result = serializer.data
        
        assert len(result['allSchedule']) == 2
        assert len(result['users']) == 1
