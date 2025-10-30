"""
Comprehensive tests for attendance app.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from rest_framework.test import force_authenticate
from django.utils.timezone import now, make_aware


@pytest.mark.django_db
class TestAttendanceUtil:
    """Tests for attendance utility functions."""

    @pytest.fixture
    def season(self):
        """Create a test season."""
        from scouting.models import Season
        return Season.objects.create(
            season=2024,
            current="y",
            void_ind="n"
        )

    @pytest.fixture
    def meeting(self, season):
        """Create a test meeting."""
        from attendance.models import Meeting
        start_time = make_aware(datetime(2024, 1, 15, 18, 0))
        end_time = make_aware(datetime(2024, 1, 15, 20, 0))
        return Meeting.objects.create(
            season=season,
            title="Test Meeting",
            description="Test Description",
            start=start_time,
            end=end_time,
            bonus=False,
            void_ind="n"
        )

    @pytest.fixture
    def approval_types(self):
        """Create attendance approval types."""
        from attendance.models import AttendanceApprovalType
        return {
            'unapp': AttendanceApprovalType.objects.create(
                approval_typ="unapp",
                approval_nm="Unapproved",
                void_ind="n"
            ),
            'app': AttendanceApprovalType.objects.create(
                approval_typ="app",
                approval_nm="Approved",
                void_ind="n"
            ),
            'rej': AttendanceApprovalType.objects.create(
                approval_typ="rej",
                approval_nm="Rejected",
                void_ind="n"
            ),
        }

    def test_get_meetings(self, season, meeting):
        """Test getting meetings for current season."""
        from attendance.util import get_meetings
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            meetings = get_meetings()
            
            assert len(meetings) == 1
            assert meetings[0].title == "Test Meeting"

    def test_get_meetings_filters_void(self, season):
        """Test that voided meetings are excluded."""
        from attendance.models import Meeting
        from attendance.util import get_meetings
        
        # Create void meeting
        Meeting.objects.create(
            season=season,
            title="Voided Meeting",
            description="Void",
            start=now(),
            end=now() + timedelta(hours=2),
            void_ind="y"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            meetings = get_meetings()
            
            assert len(meetings) == 0

    def test_save_meeting_create_new(self, season):
        """Test creating a new meeting."""
        from attendance.util import save_meeting
        
        start_time = make_aware(datetime(2024, 2, 1, 18, 0))
        end_time = make_aware(datetime(2024, 2, 1, 20, 0))
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            meeting_data = {
                "title": "New Meeting",
                "description": "Description",
                "start": start_time,
                "end": end_time,
                "bonus": False,
                "void_ind": "n"
            }
            
            result = save_meeting(meeting_data)
            
            assert result.id is not None
            assert result.title == "New Meeting"
            assert result.season == season

    def test_save_meeting_update_existing(self, season, meeting):
        """Test updating an existing meeting."""
        from attendance.util import save_meeting
        
        meeting_data = {
            "id": meeting.id,
            "title": "Updated Meeting",
            "description": "Updated",
            "start": meeting.start,
            "end": meeting.end,
            "bonus": True,
            "void_ind": "n"
        }
        
        result = save_meeting(meeting_data)
        
        assert result.id == meeting.id
        assert result.title == "Updated Meeting"
        assert result.bonus is True

    def test_get_meeting_hours(self, season):
        """Test calculating meeting hours."""
        from attendance.models import Meeting
        from attendance.util import get_meeting_hours
        
        # Create regular meeting (2 hours)
        Meeting.objects.create(
            season=season,
            title="Regular",
            description="Test",
            start=make_aware(datetime(2024, 1, 1, 18, 0)),
            end=make_aware(datetime(2024, 1, 1, 20, 0)),
            bonus=False,
            void_ind="n"
        )
        
        # Create bonus meeting (1 hour)
        Meeting.objects.create(
            season=season,
            title="Bonus",
            description="Test",
            start=make_aware(datetime(2024, 1, 2, 18, 0)),
            end=make_aware(datetime(2024, 1, 2, 19, 0)),
            bonus=True,
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            result = get_meeting_hours()
            
            assert result['hours'] == 2.0
            assert result['bonus_hours'] == 1.0

    def test_get_meeting_hours_no_end_time_raises_error(self, season):
        """Test that meeting without end time raises error."""
        from attendance.models import Meeting
        from attendance.util import get_meeting_hours
        
        Meeting.objects.create(
            season=season,
            title="No End",
            description="Test",
            start=make_aware(datetime(2024, 1, 1, 18, 0)),
            end=None,
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            with pytest.raises(Exception, match="meeting without an end time"):
                get_meeting_hours()

    def test_get_attendance(self, season, meeting, test_user, approval_types):
        """Test getting attendance records."""
        from attendance.models import Attendance
        from attendance.util import get_attendance
        
        # Create attendance record
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=meeting.end,
            absent=False,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            result = get_attendance()
            
            assert len(result) == 1
            assert result[0].user == test_user

    def test_get_attendance_filter_by_user(self, season, meeting, test_user, admin_user, approval_types):
        """Test filtering attendance by user."""
        from attendance.models import Attendance
        from attendance.util import get_attendance
        
        # Create attendance for both users
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=meeting.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        Attendance.objects.create(
            user=admin_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=meeting.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            result = get_attendance(user_id=test_user.id)
            
            assert len(result) == 1
            assert result[0].user == test_user

    def test_get_attendance_filter_by_meeting(self, season, test_user, approval_types):
        """Test filtering attendance by meeting."""
        from attendance.models import Meeting, Attendance
        from attendance.util import get_attendance
        
        meeting1 = Meeting.objects.create(
            season=season,
            title="Meeting 1",
            description="Test",
            start=make_aware(datetime(2024, 1, 1, 18, 0)),
            end=make_aware(datetime(2024, 1, 1, 20, 0)),
            void_ind="n"
        )
        meeting2 = Meeting.objects.create(
            season=season,
            title="Meeting 2",
            description="Test",
            start=make_aware(datetime(2024, 1, 2, 18, 0)),
            end=make_aware(datetime(2024, 1, 2, 20, 0)),
            void_ind="n"
        )
        
        Attendance.objects.create(
            user=test_user,
            meeting=meeting1,
            season=season,
            time_in=meeting1.start,
            time_out=meeting1.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        Attendance.objects.create(
            user=test_user,
            meeting=meeting2,
            season=season,
            time_in=meeting2.start,
            time_out=meeting2.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            result = get_attendance(meeting_id=meeting1.id)
            
            assert len(result) == 1
            assert result[0].meeting == meeting1

    def test_save_attendance_create_new(self, season, meeting, test_user, approval_types):
        """Test creating new attendance record."""
        from attendance.util import save_attendance
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            attendance_data = {
                "user": {"id": test_user.id},
                "meeting": {"id": meeting.id},
                "time_in": meeting.start,
                "time_out": meeting.end,
                "absent": False,
                "approval_typ": {"approval_typ": "app"},
                "void_ind": "n"
            }
            
            result = save_attendance(attendance_data)
            
            assert result.id is not None
            assert result.user == test_user
            assert result.meeting == meeting
            assert result.season == season

    def test_save_attendance_update_existing(self, season, meeting, test_user, approval_types):
        """Test updating existing attendance record."""
        from attendance.models import Attendance
        from attendance.util import save_attendance
        
        # Create initial attendance
        att = Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=None,
            absent=False,
            approval_typ=approval_types['unapp'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            attendance_data = {
                "id": att.id,
                "user": {"id": test_user.id},
                "meeting": {"id": meeting.id},
                "time_in": meeting.start,
                "time_out": meeting.end,
                "absent": False,
                "approval_typ": {"approval_typ": "app"},
                "void_ind": "n"
            }
            
            result = save_attendance(attendance_data)
            
            assert result.id == att.id
            assert result.time_out == meeting.end
            assert result.is_approved()

    def test_save_attendance_absent_auto_approves(self, season, meeting, test_user, approval_types):
        """Test that absent attendance is auto-approved."""
        from attendance.util import save_attendance
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            attendance_data = {
                "user": {"id": test_user.id},
                "meeting": {"id": meeting.id},
                "time_in": meeting.start,
                "absent": True,
                "approval_typ": {"approval_typ": "unapp"},
                "void_ind": "n"
            }
            
            result = save_attendance(attendance_data)
            
            assert result.absent is True
            assert result.is_approved()

    def test_save_attendance_no_timeout_approved_raises_error(self, season, meeting, test_user, approval_types):
        """Test that approving without time_out raises error."""
        from attendance.util import save_attendance
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            attendance_data = {
                "user": {"id": test_user.id},
                "meeting": {"id": meeting.id},
                "time_in": meeting.start,
                "time_out": None,
                "absent": False,
                "approval_typ": {"approval_typ": "app"},
                "void_ind": "n"
            }
            
            with pytest.raises(Exception, match="Cannot approve if no time out"):
                save_attendance(attendance_data)

    def test_save_attendance_defaults_to_unapproved(self, season, meeting, test_user, approval_types):
        """Test that attendance defaults to unapproved."""
        from attendance.util import save_attendance
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season):
            attendance_data = {
                "user": {"id": test_user.id},
                "meeting": {"id": meeting.id},
                "time_in": meeting.start,
                "time_out": meeting.end,
                "absent": False,
                "void_ind": "n"
            }
            
            result = save_attendance(attendance_data)
            
            assert result.is_unapproved()

    def test_get_attendance_report(self, season, meeting, test_user, approval_types):
        """Test generating attendance report."""
        from attendance.models import Attendance, Meeting
        from attendance.util import get_attendance_report
        
        # Create 3 meetings, 2 hours each (6 total)
        meeting2 = Meeting.objects.create(
            season=season,
            title="Meeting 2",
            description="Test",
            start=make_aware(datetime(2024, 1, 2, 18, 0)),
            end=make_aware(datetime(2024, 1, 2, 20, 0)),
            void_ind="n"
        )
        meeting3 = Meeting.objects.create(
            season=season,
            title="Meeting 3",
            description="Test",
            start=make_aware(datetime(2024, 1, 3, 18, 0)),
            end=make_aware(datetime(2024, 1, 3, 20, 0)),
            void_ind="n"
        )
        
        # User attended 2 out of 3 (4 hours = 66.67%)
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=meeting.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        Attendance.objects.create(
            user=test_user,
            meeting=meeting2,
            season=season,
            time_in=meeting2.start,
            time_out=meeting2.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.util.user.util.get_users', return_value=[test_user]):
            result = get_attendance_report()
            
            assert len(result) == 1
            assert result[0]['user'] == test_user
            assert result[0]['time'] == 4.0
            assert result[0]['percentage'] == 67.0  # 4/6 * 100 = 66.67 rounded to 67

    def test_get_attendance_report_only_approved_counted(self, season, meeting, test_user, approval_types):
        """Test that only approved attendance is counted."""
        from attendance.models import Attendance
        from attendance.util import get_attendance_report
        
        # Create approved attendance
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=meeting.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        # Create unapproved attendance (should not count)
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start + timedelta(days=1),
            time_out=meeting.end + timedelta(days=1),
            approval_typ=approval_types['unapp'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.util.user.util.get_users', return_value=[test_user]):
            result = get_attendance_report()
            
            assert len(result) == 1
            assert result[0]['time'] == 2.0  # Only the approved 2-hour meeting

    def test_get_attendance_report_absent_not_counted(self, season, meeting, test_user, approval_types):
        """Test that absent records are not counted in time."""
        from attendance.models import Attendance
        from attendance.util import get_attendance_report
        
        # Create absent attendance (approved but absent)
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            absent=True,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.util.user.util.get_users', return_value=[test_user]):
            result = get_attendance_report()
            
            assert len(result) == 1
            assert result[0]['time'] == 0.0  # Absent not counted


@pytest.mark.django_db
class TestAttendanceViews:
    """Tests for attendance views."""

    @pytest.fixture
    def season(self):
        """Create a test season."""
        from scouting.models import Season
        return Season.objects.create(
            season=2024,
            current="y",
            void_ind="n"
        )

    @pytest.fixture
    def meeting(self, season):
        """Create a test meeting."""
        from attendance.models import Meeting
        start_time = make_aware(datetime(2024, 1, 15, 18, 0))
        end_time = make_aware(datetime(2024, 1, 15, 20, 0))
        return Meeting.objects.create(
            season=season,
            title="Test Meeting",
            description="Test Description",
            start=start_time,
            end=end_time,
            bonus=False,
            void_ind="n"
        )

    @pytest.fixture
    def approval_types(self):
        """Create attendance approval types."""
        from attendance.models import AttendanceApprovalType
        return {
            'unapp': AttendanceApprovalType.objects.create(
                approval_typ="unapp",
                approval_nm="Unapproved",
                void_ind="n"
            ),
            'app': AttendanceApprovalType.objects.create(
                approval_typ="app",
                approval_nm="Approved",
                void_ind="n"
            ),
        }

    def test_attendance_view_get(self, api_rf, test_user, season, meeting, approval_types):
        """Test AttendanceView GET."""
        from attendance.views import AttendanceView
        from attendance.models import Attendance
        
        # Create attendance record
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=meeting.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.views.access_response') as mock_access:
            # Setup mock to call the function
            def call_fun(path, user_id, auth_obj, error_msg, fun):
                return fun()
            mock_access.side_effect = call_fun
            
            request = api_rf.get('/attendance/attendance/')
            force_authenticate(request, user=test_user)
            view = AttendanceView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert len(response.data) == 1

    def test_attendance_view_post(self, api_rf, test_user, season, meeting, approval_types):
        """Test AttendanceView POST."""
        from attendance.views import AttendanceView
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.views.access_response') as mock_access:
            # Setup mock to call the function
            def call_fun(path, user_id, auth_obj, error_msg, fun):
                return fun()
            mock_access.side_effect = call_fun
            
            data = {
                "user": {"id": test_user.id, "username": test_user.username},
                "meeting": {"id": meeting.id},
                "time_in": meeting.start.isoformat(),
                "time_out": meeting.end.isoformat(),
                "absent": False,
                "approval_typ": {"approval_typ": "app", "approval_nm": "Approved"},
                "void_ind": "n"
            }
            
            request = api_rf.post('/attendance/attendance/', data, format='json')
            force_authenticate(request, user=test_user)
            view = AttendanceView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_meetings_view_get(self, api_rf, test_user, season, meeting):
        """Test MeetingsView GET."""
        from attendance.views import MeetingsView
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.views.access_response') as mock_access:
            # Setup mock to call the function
            def call_fun(path, user_id, auth_obj, error_msg, fun):
                return fun()
            mock_access.side_effect = call_fun
            
            request = api_rf.get('/attendance/meetings/')
            force_authenticate(request, user=test_user)
            view = MeetingsView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert len(response.data) == 1
            assert response.data[0]['title'] == "Test Meeting"

    def test_meetings_view_post(self, api_rf, test_user, season):
        """Test MeetingsView POST."""
        from attendance.views import MeetingsView
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.views.access_response') as mock_access:
            # Setup mock to call the function
            def call_fun(path, user_id, auth_obj, error_msg, fun):
                return fun()
            mock_access.side_effect = call_fun
            
            start_time = make_aware(datetime(2024, 2, 1, 18, 0))
            end_time = make_aware(datetime(2024, 2, 1, 20, 0))
            
            data = {
                "title": "New Meeting",
                "description": "Test",
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "bonus": False,
                "void_ind": "n"
            }
            
            request = api_rf.post('/attendance/meetings/', data, format='json')
            force_authenticate(request, user=test_user)
            view = MeetingsView.as_view()
            response = view(request)
            
            assert response.status_code == 200

    def test_attendance_report_view_get(self, api_rf, test_user, season, meeting, approval_types):
        """Test AttendanceReportView GET."""
        from attendance.views import AttendanceReportView
        from attendance.models import Attendance
        
        # Create attendance
        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=meeting.start,
            time_out=meeting.end,
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.util.user.util.get_users', return_value=[test_user]), \
             patch('attendance.views.access_response') as mock_access:
            # Setup mock to call the function
            def call_fun(path, user_id, auth_obj, error_msg, fun):
                return fun()
            mock_access.side_effect = call_fun
            
            request = api_rf.get('/attendance/attendance-report/')
            force_authenticate(request, user=test_user)
            view = AttendanceReportView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert len(response.data) == 1

    def test_meeting_hours_view_get(self, api_rf, test_user, season, meeting):
        """Test MeetingHoursView GET."""
        from attendance.views import MeetingHoursView
        
        with patch('attendance.util.scouting.util.get_current_season', return_value=season), \
             patch('attendance.views.access_response') as mock_access:
            # Setup mock to call the function
            def call_fun(path, user_id, auth_obj, error_msg, fun):
                return fun()
            mock_access.side_effect = call_fun
            
            request = api_rf.get('/attendance/meeting-hours/')
            force_authenticate(request, user=test_user)
            view = MeetingHoursView.as_view()
            response = view(request)
            
            assert response.status_code == 200
            assert 'hours' in response.data
            assert 'bonus_hours' in response.data


@pytest.mark.django_db
class TestAttendanceModels:
    """Tests for attendance models."""

    @pytest.fixture
    def season(self):
        """Create a test season."""
        from scouting.models import Season
        return Season.objects.create(
            season=2024,
            current="y",
            void_ind="n"
        )

    @pytest.fixture
    def approval_types(self):
        """Create attendance approval types."""
        from attendance.models import AttendanceApprovalType
        return {
            'unapp': AttendanceApprovalType.objects.create(
                approval_typ="unapp",
                approval_nm="Unapproved",
                void_ind="n"
            ),
            'app': AttendanceApprovalType.objects.create(
                approval_typ="app",
                approval_nm="Approved",
                void_ind="n"
            ),
            'rej': AttendanceApprovalType.objects.create(
                approval_typ="rej",
                approval_nm="Rejected",
                void_ind="n"
            ),
        }

    def test_attendance_approval_type_str(self, approval_types):
        """Test AttendanceApprovalType string representation."""
        assert str(approval_types['app']) == "app : Approved"

    def test_attendance_is_approved(self, season, test_user, approval_types):
        """Test Attendance is_approved method."""
        from attendance.models import Attendance
        
        attendance = Attendance.objects.create(
            user=test_user,
            season=season,
            time_in=now(),
            approval_typ=approval_types['app'],
            void_ind="n"
        )
        
        assert attendance.is_approved() is True
        assert attendance.is_unapproved() is False
        assert attendance.is_rejected() is False

    def test_attendance_is_unapproved(self, season, test_user, approval_types):
        """Test Attendance is_unapproved method."""
        from attendance.models import Attendance
        
        attendance = Attendance.objects.create(
            user=test_user,
            season=season,
            time_in=now(),
            approval_typ=approval_types['unapp'],
            void_ind="n"
        )
        
        assert attendance.is_unapproved() is True
        assert attendance.is_approved() is False
        assert attendance.is_rejected() is False

    def test_attendance_is_rejected(self, season, test_user, approval_types):
        """Test Attendance is_rejected method."""
        from attendance.models import Attendance
        
        attendance = Attendance.objects.create(
            user=test_user,
            season=season,
            time_in=now(),
            approval_typ=approval_types['rej'],
            void_ind="n"
        )
        
        assert attendance.is_rejected() is True
        assert attendance.is_approved() is False
        assert attendance.is_unapproved() is False
