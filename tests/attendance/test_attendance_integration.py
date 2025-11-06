"""
Complex integration tests for attendance tracking workflows.

This test file validates:
- Meeting creation and queries
- Bulk operations for efficiency
- Date-range queries
"""
import pytest
from datetime import datetime, timedelta


@pytest.mark.django_db
class TestComplexAttendanceWorkflows:
    """Complex integration tests for attendance tracking with approval workflows."""

    @pytest.fixture
    def meeting_type(self):
        """Create a meeting type."""
        from attendance.models import MeetingType
        return MeetingType.objects.create(
            meeting_typ="reg",
            meeting_nm="Regular Meeting",
            void_ind="n"
        )

    def test_meeting_creation_and_queries(self, meeting_type):
        """Test creating meetings and querying them efficiently."""
        from attendance.models import Meeting
        from scouting.models import Season
        
        # Setup: Create season
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        
        # Create multiple meetings
        meeting1 = Meeting.objects.create(
            season=season,
            meeting_typ=meeting_type,
            title='Weekly Meeting 1',
            description='First team meeting',
            start=datetime(2024, 3, 1, 18, 0, 0),
            end=datetime(2024, 3, 1, 20, 0, 0)
        )
        
        meeting2 = Meeting.objects.create(
            season=season,
            meeting_typ=meeting_type,
            title='Weekly Meeting 2',
            description='Second team meeting',
            start=datetime(2024, 3, 8, 18, 0, 0),
            end=datetime(2024, 3, 8, 20, 0, 0)
        )
        
        # Test: Query meetings for the season
        season_meetings = Meeting.objects.filter(season=season).order_by('start')
        
        assert season_meetings.count() == 2
        assert season_meetings[0].title == 'Weekly Meeting 1'
        assert season_meetings[1].title == 'Weekly Meeting 2'

    def test_bulk_meeting_creation(self, meeting_type):
        """Test bulk operations on meeting records."""
        from attendance.models import Meeting
        from scouting.models import Season
        
        # Setup: Create season
        season = Season.objects.create(
            season='2024',
            current='y',
            game='Test Game',
            manual=''
        )
        
        # Bulk create meetings
        meetings = []
        base_date = datetime(2024, 3, 1, 14, 0, 0)
        for i in range(10):
            meeting = Meeting(
                season=season,
                meeting_typ=meeting_type,
                title=f'Workshop {i+1}',
                description=f'Workshop session {i+1}',
                start=base_date + timedelta(days=i*7),
                end=base_date + timedelta(days=i*7, hours=3)
            )
            meetings.append(meeting)
        
        # Bulk insert
        Meeting.objects.bulk_create(meetings)
        
        # Verify bulk creation
        total_meetings = Meeting.objects.filter(season=season).count()
        assert total_meetings == 10
        
        # Test querying meetings by date range
        end_date = base_date + timedelta(days=30)
        meetings_in_range = Meeting.objects.filter(
            season=season,
            start__gte=base_date,
            start__lte=end_date
        ).count()
        assert meetings_in_range > 0
