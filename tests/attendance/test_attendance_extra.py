"""
Extra coverage tests for attendance app.
Covers:
  - attendance/util.py line 163  (exempt meeting reduces user_total)
  - attendance/util.py lines 289-297 (end_meeting absent loop)
  - attendance/views.py lines 84-85 (save_attendance success path)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.utils.timezone import make_aware, now


# ---------------------------------------------------------------------------
# attendance/util.py line 163
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetHoursExemptPath:
    """Tests exempt attendance path in get_hours (line 163)."""

    def test_exempt_regular_meeting_reduces_user_total(self, test_user):
        """Line 163: exempt 'reg' meeting subtracts from user_total."""
        from attendance.models import MeetingType, Meeting, AttendanceApprovalType, Attendance
        from scouting.models import Season

        season = Season.objects.create(season="2099a", current="y", game="G", manual="M")
        mt_reg = MeetingType.objects.create(meeting_typ="reg", meeting_nm="Reg Exempt", void_ind="n")
        atype_exmpt = AttendanceApprovalType.objects.create(
            approval_typ="exmpt", approval_nm="Exempt", void_ind="n"
        )

        start = make_aware(datetime(2099, 1, 1, 18, 0))
        end = make_aware(datetime(2099, 1, 1, 20, 0))
        meeting = Meeting.objects.create(
            season=season,
            meeting_typ=mt_reg,
            title="Exempt Test Meeting",
            description="desc",
            start=start,
            end=end,
            ended=True,
            void_ind="n",
        )

        Attendance.objects.create(
            user=test_user,
            meeting=meeting,
            season=season,
            time_in=start,
            time_out=end,
            absent=False,
            approval_typ=atype_exmpt,
            void_ind="n",
        )

        with patch("attendance.util.scouting.util.get_current_season", return_value=season), \
             patch("attendance.util.get_meeting_hours", return_value={"hours": 10.0, "event_hours": 5.0}), \
             patch("attendance.util.user.util.get_users") as mock_users:
            mock_users.return_value = [test_user]
            from attendance.util import get_attendance_report
            result = get_attendance_report(user_id=test_user.id)

        assert len(result) == 1
        # exempt reg meeting reduced user_total (10.0 - 2.0 = 8.0)
        assert result[0]["req_reg_time"] == pytest.approx(8.0, abs=0.01)


# ---------------------------------------------------------------------------
# attendance/util.py lines 289-297 (end_meeting absent loop)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestEndMeeting:
    """Test end_meeting function – lines 289-297 (absent records for missing users)."""

    def test_end_meeting_creates_absent_records(self, test_user):
        """Lines 288-297: for each user not already in attendance, save absent record."""
        from attendance.models import MeetingType, Meeting, AttendanceApprovalType
        from scouting.models import Season
        from attendance.util import end_meeting

        season = Season.objects.create(season="2099b", current="y", game="G", manual="M")
        mt = MeetingType.objects.create(meeting_typ="reg_em", meeting_nm="Reg EM", void_ind="n")
        # AttendanceApprovalType "app" must exist for save_attendance
        atype = AttendanceApprovalType.objects.create(
            approval_typ="app", approval_nm="Approved", void_ind="n"
        )
        start = make_aware(datetime(2099, 2, 1, 18, 0))
        end_dt = make_aware(datetime(2099, 2, 1, 20, 0))
        meeting = Meeting.objects.create(
            season=season,
            meeting_typ=mt,
            title="End Meeting Test",
            description="d",
            start=start,
            end=end_dt,
            ended=False,
            void_ind="n",
        )

        with patch("attendance.util.scouting.util.get_current_season", return_value=season), \
             patch("attendance.util.user.util.get_users") as mock_get_users, \
             patch("attendance.util.save_attendance") as mock_save:
            mock_get_users.return_value.filter.return_value = [test_user]
            end_meeting(meeting.id)

        # save_attendance should have been called once for the user
        mock_save.assert_called_once()
        call_args = mock_save.call_args[0][0]
        assert call_args["absent"] is True
        assert call_args["void_ind"] == "n"


# ---------------------------------------------------------------------------
# attendance/views.py lines 84-85 (success path)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestAttendanceViewPost:
    """Test POST /attendance/attendance/ success path (lines 84-85)."""

    url = "/attendance/attendance/"

    def test_post_saves_and_returns_attendance(self, api_client, test_user):
        """Lines 84-85: valid data → save_attendance called, Response returned."""
        from attendance.models import MeetingType, Meeting, AttendanceApprovalType
        from scouting.models import Season
        from attendance.models import Attendance

        season = Season.objects.create(season="2099c", current="y", game="G", manual="M")
        mt = MeetingType.objects.create(meeting_typ="reg_vp", meeting_nm="Reg VP", void_ind="n")
        atype = AttendanceApprovalType.objects.create(
            approval_typ="app", approval_nm="Approved", void_ind="n"
        )
        start = make_aware(datetime(2099, 3, 1, 18, 0))
        end_dt = make_aware(datetime(2099, 3, 1, 20, 0))
        meeting = Meeting.objects.create(
            season=season, meeting_typ=mt, title="VP Meeting", description="d",
            start=start, end=end_dt, ended=False, void_ind="n",
        )

        # Create a mock Attendance object to return from save_attendance
        mock_att = MagicMock(spec=Attendance)
        mock_att.id = 999
        mock_att.user = test_user
        mock_att.meeting = meeting
        mock_att.season = season
        mock_att.time_in = start
        mock_att.time_out = end_dt
        mock_att.absent = False
        mock_att.approval_typ = atype
        mock_att.void_ind = "n"

        api_client.force_authenticate(user=test_user)

        payload = {
            "user": {"id": test_user.id},
            "meeting": {"id": meeting.id},
            "time_in": start.isoformat(),
            "absent": False,
            "approval_typ": {"approval_typ": "app"},
            "void_ind": "n",
        }

        with patch("attendance.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()), \
             patch("attendance.views.attendance.util.save_attendance", return_value=mock_att):
            response = api_client.post(self.url, payload, format="json")

        assert response.status_code == 200
