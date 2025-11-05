"""
Comprehensive tests for Attendance model methods to increase coverage.
"""
import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestAttendanceModelStringMethods:
    """Test __str__ methods for attendance app models."""
    
    def test_meeting_type_str(self):
        """Test MeetingType __str__ method."""
        from attendance.models import MeetingType
        
        meeting_type = MeetingType.objects.create(
            meeting_typ="team",
            meeting_nm="Team Meeting"
        )
        str_result = str(meeting_type)
        assert "team" in str_result
        assert "Team Meeting" in str_result
    
    def test_meeting_str(self):
        """Test Meeting __str__ method."""
        from attendance.models import Meeting, MeetingType
        from scouting.models import Season
        
        season = Season.objects.create(
            season=2024,
            current="y"
        )
        
        meeting_type = MeetingType.objects.create(
            meeting_typ="build",
            meeting_nm="Build Session"
        )
        
        meeting = Meeting.objects.create(
            season=season,
            meeting_typ=meeting_type,
            title="Weekend Build",
            description="Saturday build session",
            start=timezone.now()
        )
        
        str_result = str(meeting)
        assert str(meeting.id) in str_result
        assert "Weekend Build" in str_result
    
    def test_attendance_approval_type_str(self):
        """Test AttendanceApprovalType __str__ method."""
        from attendance.models import AttendanceApprovalType
        
        approval_type = AttendanceApprovalType.objects.create(
            approval_typ="app",
            approval_nm="Approved"
        )
        str_result = str(approval_type)
        assert "app" in str_result
        assert "Approved" in str_result
    
    def test_attendance_str(self):
        """Test Attendance __str__ method."""
        from attendance.models import Attendance, Meeting, MeetingType, AttendanceApprovalType
        from scouting.models import Season
        from user.models import User
        
        user = User.objects.create_user(
            username="attendee",
            email="attendee@test.com",
            password="pass123"
        )
        
        season = Season.objects.create(
            season=2024,
            current="y"
        )
        
        meeting_type = MeetingType.objects.create(
            meeting_typ="team",
            meeting_nm="Team Meeting"
        )
        
        meeting = Meeting.objects.create(
            season=season,
            meeting_typ=meeting_type,
            title="Test Meeting",
            description="Test description",
            start=timezone.now()
        )
        
        approval_type = AttendanceApprovalType.objects.create(
            approval_typ="unapp",
            approval_nm="Unapproved"
        )
        
        attendance = Attendance.objects.create(
            user=user,
            meeting=meeting,
            season=season,
            approval_typ=approval_type
        )
        
        str_result = str(attendance)
        assert str(attendance.id) in str_result


@pytest.mark.django_db
class TestAttendanceModelMethods:
    """Test Attendance model business logic methods."""
    
    def test_is_unapproved(self):
        """Test Attendance is_unapproved method."""
        from attendance.models import Attendance, AttendanceApprovalType
        from scouting.models import Season
        from user.models import User
        
        user = User.objects.create_user(
            username="unappuser",
            email="unapp@test.com",
            password="pass123"
        )
        
        season = Season.objects.create(
            season=2024,
            current="y"
        )
        
        # Create unapproved attendance
        unapp_type = AttendanceApprovalType.objects.create(
            approval_typ="unapp",
            approval_nm="Unapproved"
        )
        
        attendance = Attendance.objects.create(
            user=user,
            season=season,
            approval_typ=unapp_type
        )
        
        assert attendance.is_unapproved() is True
        assert attendance.is_approved() is False
        assert attendance.is_rejected() is False
    
    def test_is_approved(self):
        """Test Attendance is_approved method."""
        from attendance.models import Attendance, AttendanceApprovalType
        from scouting.models import Season
        from user.models import User
        
        user = User.objects.create_user(
            username="appuser",
            email="app@test.com",
            password="pass123"
        )
        
        season = Season.objects.create(
            season=2024,
            current="y"
        )
        
        # Create approved attendance
        app_type = AttendanceApprovalType.objects.create(
            approval_typ="app",
            approval_nm="Approved"
        )
        
        attendance = Attendance.objects.create(
            user=user,
            season=season,
            approval_typ=app_type
        )
        
        assert attendance.is_approved() is True
        assert attendance.is_unapproved() is False
        assert attendance.is_rejected() is False
    
    def test_is_rejected(self):
        """Test Attendance is_rejected method."""
        from attendance.models import Attendance, AttendanceApprovalType
        from scouting.models import Season
        from user.models import User
        
        user = User.objects.create_user(
            username="rejuser",
            email="rej@test.com",
            password="pass123"
        )
        
        season = Season.objects.create(
            season=2024,
            current="y"
        )
        
        # Create rejected attendance
        rej_type = AttendanceApprovalType.objects.create(
            approval_typ="rej",
            approval_nm="Rejected"
        )
        
        attendance = Attendance.objects.create(
            user=user,
            season=season,
            approval_typ=rej_type
        )
        
        assert attendance.is_rejected() is True
        assert attendance.is_approved() is False
        assert attendance.is_unapproved() is False


@pytest.mark.django_db
class TestAttendanceModelFields:
    """Test attendance model field behaviors."""
    
    def test_meeting_type_void_default(self):
        """Test MeetingType void_ind default value."""
        from attendance.models import MeetingType
        
        meeting_type = MeetingType.objects.create(
            meeting_typ="test",
            meeting_nm="Test Meeting Type"
        )
        
        assert meeting_type.void_ind == "n"
    
    def test_meeting_void_default(self):
        """Test Meeting void_ind default value."""
        from attendance.models import Meeting, MeetingType
        from scouting.models import Season
        
        season = Season.objects.create(
            season=2024,
            current="y"
        )
        
        meeting_type = MeetingType.objects.create(
            meeting_typ="test",
            meeting_nm="Test Meeting Type"
        )
        
        meeting = Meeting.objects.create(
            season=season,
            meeting_typ=meeting_type,
            title="Test Meeting",
            description="Test"
        )
        
        assert meeting.void_ind == "n"
    
    def test_attendance_absent_default(self):
        """Test Attendance absent default value."""
        from attendance.models import Attendance, AttendanceApprovalType
        from scouting.models import Season
        from user.models import User
        
        user = User.objects.create_user(
            username="absentuser",
            email="absent@test.com",
            password="pass123"
        )
        
        season = Season.objects.create(
            season=2024,
            current="y"
        )
        
        approval_type = AttendanceApprovalType.objects.create(
            approval_typ="unapp",
            approval_nm="Unapproved"
        )
        
        attendance = Attendance.objects.create(
            user=user,
            season=season,
            approval_typ=approval_type
        )
        
        assert attendance.absent is False
        assert attendance.void_ind == "n"
