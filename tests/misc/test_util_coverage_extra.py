"""
Coverage tests for scouting/admin/util.py, tba/util.py, scouting/strategizing/util.py,
and attendance/util.py (end_meeting).
"""
import pytest
from unittest.mock import patch, MagicMock
import datetime
import pytz


def ensure_admin_group():
    """Create Admin group if it doesn't exist."""
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name="Admin")


# =============================================================================
# scouting/admin/util.py
# =============================================================================

@pytest.mark.django_db
class TestScoutAdminUtilExtra:
    """Cover scouting admin util gaps."""

    def test_delete_event_with_field_responses(self, test_user):
        """Lines 108-144: delete_event removes field/pit responses and associated data."""
        from scouting.admin.util import delete_event
        from scouting.models import Season, Event, Team, FieldResponse, CompetitionLevel, Match
        from form.models import FormType, Response as FormResp

        season = Season.objects.create(season="2025de", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="DEL", event_cd="2025dest", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        team = Team.objects.create(team_no=5551, team_nm="DelTeam", void_ind="n")
        team.event_set.add(event)
        cl, _ = CompetitionLevel.objects.get_or_create(
            comp_lvl_typ="qmde", defaults={"comp_lvl_typ_nm": "Qual DE", "comp_lvl_order": 1, "void_ind": "n"}
        )
        match = Match.objects.create(
            match_key="2025dest_qm1", match_number=1,
            event=event, comp_level=cl, void_ind="n"
        )
        ft, _ = FormType.objects.get_or_create(
            form_typ="delft", defaults={"form_nm": "Del Form"}
        )
        resp = FormResp.objects.create(form_typ=ft, void_ind="n")
        FieldResponse.objects.create(
            event=event, team=team, user=test_user, match=match,
            response=resp, void_ind="n"
        )

        result = delete_event(event.id)
        assert result is not None

    def test_delete_season_cascade(self):
        """Lines 214, 218-229: delete_season iterates events and scout questions."""
        from scouting.admin.util import delete_season
        from scouting.models import Season
        season = Season.objects.create(season="2025ds", current="n", game="G", manual="")
        result = delete_season(season.id)
        assert result is not None

    def test_save_event_update_existing(self):
        """Line 263: save_event with existing event_id."""
        from scouting.admin.util import save_event
        from scouting.models import Season, Event
        season = Season.objects.create(season="2025seu", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="Old", event_cd="2025seust", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        result = save_event({
            "event_id": event.id,
            "event_nm": "Updated",
            "event_cd": "2025seust",
            "date_st": datetime.datetime.now(pytz.UTC),
            "date_end": datetime.datetime.now(pytz.UTC),
            "timezone": "America/New_York",
            "current": "n",
            "void_ind": "n",
            "season_id": season.id,
        })
        assert result.event_nm == "Updated"

    def test_link_team_to_event_checked_true(self):
        """Lines 369-389: link_team_to_event adds team."""
        from scouting.admin.util import link_team_to_event
        from scouting.models import Season, Event, Team
        season = Season.objects.create(season="2025lte", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="LTE", event_cd="2025ltest", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        team = Team.objects.create(team_no=5552, team_nm="LTETeam", void_ind="n")
        data = {
            "event_id": event.id,
            "teams": [{"team_no": 5552, "team_nm": "LTETeam", "checked": True}]
        }
        result = link_team_to_event(data)
        assert "ADD" in result

    def test_save_scout_schedule_new(self):
        """Lines 460-486: save_scout_schedule creates new entry."""
        from scouting.admin.util import save_scout_schedule
        from scouting.models import Season, Event
        season = Season.objects.create(season="2025sss", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="SSS", event_cd="2025sssst", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        now = datetime.datetime.now(pytz.UTC)
        result = save_scout_schedule({
            "event_id": event.id,
            "st_time": now,
            "end_time": now + datetime.timedelta(hours=1),
            "void_ind": "n",
        })
        assert result.id is not None

    def test_save_schedule_new(self, test_user):
        """Lines 508-531: save_schedule creates new schedule entry."""
        from scouting.admin.util import save_schedule
        from scouting.models import Season, Event, ScheduleType
        season = Season.objects.create(season="2025scn", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="SCN", event_cd="2025scnst",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
            current="y",
        )
        sch_typ = ScheduleType.objects.create(sch_typ="genschn", sch_nm="General SCN")
        now = datetime.datetime.now(pytz.UTC)
        with patch("scouting.admin.util.scouting.util.get_current_event", return_value=event):
            result = save_schedule({
                "user": test_user.id,
                "sch_typ": "genschn",
                "st_time": now,
                "end_time": now + datetime.timedelta(hours=2),
                "void_ind": "n",
            })
        assert result.id is not None

    def test_get_scouting_user_info_creates_missing(self, test_user):
        """Lines 580-586: get_scouting_user_info creates UserInfo if missing."""
        from scouting.admin.util import get_scouting_user_info
        from scouting.models import UserInfo
        ensure_admin_group()
        UserInfo.objects.filter(user=test_user, void_ind="n").delete()
        result = get_scouting_user_info()
        # Result is a list of UserInfo objects for all active non-admin users
        assert isinstance(result, list)

    def test_save_field_form_with_image_ids(self):
        """Lines 679, 683, 687, 692-713: save_field_form with image ID data (no uploads)."""
        from scouting.admin.util import save_field_form
        from scouting.models import Season
        season = Season.objects.create(season="2025sff", current="y", game="G", manual="")
        with patch("scouting.admin.util.scouting.util.get_current_season", return_value=season):
            result = save_field_form({
                "img_id": "test_img_id",
                "img_ver": 123,
                "inv_img_id": "test_inv_id",
                "inv_img_ver": 456,
                "full_img_id": "test_full_id",
                "full_img_ver": 789,
            })
        assert result is not None
        assert result.img_id == "test_img_id"

    def test_scouting_report(self):
        """Lines 725-835: scouting_report with mocked external calls."""
        from scouting.admin.util import scouting_report
        from scouting.models import Team, Season, Event
        team_3492, _ = Team.objects.get_or_create(
            team_no=3492, defaults={"team_nm": "Team 3492", "void_ind": "n"}
        )
        season = Season.objects.create(season="2025sr", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="SR", event_cd="2025srst", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        team_3492.event_set.add(event)
        with patch("scouting.admin.util.tba.util.get_events_for_team", return_value=[]), \
             patch("scouting.admin.util.scouting.util.get_current_season", return_value=season):
            result = scouting_report()
        assert result is not None


# =============================================================================
# tba/util.py
# =============================================================================

@pytest.mark.django_db
class TestTBAUtilCoverage:
    """Cover tba/util.py gaps."""

    def test_get_events_for_team_empty(self):
        """Lines 406-484 area: get_events_for_team with empty TBA response."""
        from tba.util import get_events_for_team
        from scouting.models import Team, Season
        team = Team.objects.create(team_no=9999, team_nm="TBATeam", void_ind="n")
        season = Season.objects.create(season="2025tba", current="n", game="G", manual="")
        with patch("tba.util.requests.get") as mock_get:
            from json import dumps
            mock_get.return_value.text = dumps([])
            result = get_events_for_team(team, season)
        assert isinstance(result, list)
        assert result == []

    def test_replace_frc_in_str(self):
        """Lines 517-521: replace_frc_in_str utility."""
        from tba.util import replace_frc_in_str
        result = replace_frc_in_str("frc3492")
        assert "frc" not in result
        assert "3492" in result

    def test_sync_season_mocked(self):
        """Lines 85-110: sync_season with mocked TBA."""
        from tba.util import sync_season
        from scouting.models import Season, Team
        season = Season.objects.create(season="2025ts", current="n", game="G", manual="")
        Team.objects.get_or_create(team_no=3492, defaults={"team_nm": "T3492", "void_ind": "n"})
        with patch("tba.util.requests.get") as mock_get, \
             patch("tba.util.sync_event") as mock_sync_event:
            from json import dumps
            mock_get.return_value.text = dumps([
                {"key": "2025test", "name": "Test Event"}
            ])
            mock_sync_event.return_value = "Synced"
            result = sync_season(season.id)
        assert result is not None

    def test_get_tba_event(self):
        """Lines 111-163: get_tba_event parses event data."""
        from tba.util import get_tba_event
        from json import dumps
        with patch("tba.util.requests.get") as mock_get:
            mock_get.return_value.text = dumps({
                "key": "2025test", "name": "Test Event",
                "start_date": "2025-01-01", "end_date": "2025-01-02",
                "timezone": "America/New_York",
                "webcasts": [],
                "event_url": None, "gmaps_url": None, "address": None,
                "city": None, "state_prov": None, "postal_code": None,
                "location_name": None,
            })
            result = get_tba_event("2025test")
        assert result is not None
        assert result["event_cd"] == "2025test"

    def test_sync_event_team_info_with_mock(self):
        """Lines 343-392: sync_event_team_info."""
        from tba.util import sync_event_team_info
        from scouting.models import Event, Season
        from json import dumps
        season = Season.objects.create(season="2025sti", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="STI", event_cd="2025stist", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        with patch("tba.util.get_tba_event") as mock_gta_event, \
             patch("tba.util.get_tba_event_teams", return_value=[]), \
             patch("tba.util.get_tba_event_team_info", return_value=[]), \
             patch("tba.util.Team.objects.get_or_create", return_value=(MagicMock(), True)):
            mock_gta_event.return_value = {
                "event_nm": "STI", "event_cd": "2025stist",
                "date_st": datetime.datetime.now(pytz.UTC),
                "date_end": datetime.datetime.now(pytz.UTC),
                "timezone": "America/New_York", "teams": [],
                "event_url": None, "gmaps_url": None, "address": None,
                "city": None, "state_prov": None, "postal_code": None,
                "location_name": None, "webcast_url": "",
            }
            with patch("tba.util.requests.get") as mock_get:
                mock_get.return_value.text = dumps([])
                result = sync_event_team_info(force=0)
        assert result is not None


# =============================================================================
# scouting/strategizing/util.py
# =============================================================================

@pytest.mark.django_db
class TestStrategizingUtilCoverage:
    """Cover scouting/strategizing/util.py gaps."""

    def test_get_team_notes_no_event(self):
        """Line 49: get_team_notes when event has no notes."""
        from scouting.strategizing.util import get_team_notes
        from scouting.models import Season, Event
        season = Season.objects.create(season="2025gtn", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="GTN", event_cd="2025gtnst", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        with patch("scouting.strategizing.util.scouting.util.get_current_event", return_value=event):
            result = get_team_notes()
        assert isinstance(result, list)

    def test_get_match_strategies_all(self):
        """Lines 92-104: get_match_strategies returns all strategies."""
        from scouting.strategizing.util import get_match_strategies
        from scouting.models import Season, Event
        season = Season.objects.create(season="2025gms", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="GMS", event_cd="2025gmsst", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        with patch("scouting.strategizing.util.scouting.util.get_current_event", return_value=event):
            result = get_match_strategies()
        assert isinstance(result, list)

    def test_save_note(self, test_user):
        """Line 123: save_note creates a new note."""
        from scouting.strategizing.util import save_note
        from scouting.models import Season, Event, Team
        season = Season.objects.create(season="2025sn", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="SN", event_cd="2025snst", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        team = Team.objects.create(team_no=7771, team_nm="SNTeam", void_ind="n")
        team.event_set.add(event)
        data = {
            "id": None,
            "team_id": team.team_no,
            "note": "Test note",
            "void_ind": "n",
        }
        with patch("scouting.strategizing.util.scouting.util.get_current_event", return_value=event), \
             patch("general.cloudinary.build_image_url", return_value=None):
            result = save_note(data, test_user)
        assert result is not None

    def test_get_alliance_selections_empty(self):
        """Line 151: get_alliance_selections returns queryset."""
        from scouting.strategizing.util import get_alliance_selections
        from scouting.models import Season, Event
        season = Season.objects.create(season="2025gas", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="GAS", event_cd="2025gasst", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n",
        )
        with patch("scouting.strategizing.util.scouting.util.get_current_event", return_value=event):
            result = get_alliance_selections()
        assert result is not None

    def test_get_dashboard_view_types(self):
        """Line 175: get_dashboard_view_types returns queryset."""
        from scouting.strategizing.util import get_dashboard_view_types
        result = get_dashboard_view_types()
        assert result is not None

    def test_get_dashboard_creates_new(self, test_user):
        """Lines 184, 187-188: get_dashboard creates new dashboard when none exists."""
        from scouting.strategizing.util import get_dashboard
        from scouting.models import Season, DashboardViewType
        season = Season.objects.create(season="2025gd", current="y", game="G", manual="")
        # Need a DashboardViewType with "main"
        DashboardViewType.objects.get_or_create(
            dash_view_typ="main", defaults={"dash_view_nm": "Main"}
        )
        with patch("scouting.strategizing.util.scouting.util.get_current_season", return_value=season):
            result = get_dashboard(test_user.id)
        assert result is not None
        assert "id" in result


# =============================================================================
# attendance/util.py - Missing lines 279-297 (end_meeting) and 250 (get_attendance)
# =============================================================================

@pytest.mark.django_db
class TestAttendanceEndMeeting:
    """Cover attendance/util.py end_meeting lines 279-297."""

    def test_end_meeting(self, test_user):
        """Lines 279-297: end_meeting marks users absent."""
        from attendance.util import end_meeting
        from attendance.models import Meeting, MeetingType, AttendanceApprovalType
        from scouting.models import Season
        ensure_admin_group()
        season = Season.objects.create(season="2024em", current="y", game="G", manual="")
        mt, _ = MeetingType.objects.get_or_create(
            meeting_typ="regem", defaults={"meeting_nm": "Regular EM"}
        )
        now = datetime.datetime.now(pytz.UTC)
        meeting = Meeting.objects.create(
            season=season, meeting_typ=mt, title="EM Meeting",
            description="", start=now, end=now + datetime.timedelta(hours=2),
            ended=False
        )
        AttendanceApprovalType.objects.get_or_create(
            approval_typ="app", defaults={"approval_nm": "Approved"}
        )
        AttendanceApprovalType.objects.get_or_create(
            approval_typ="unapp", defaults={"approval_nm": "Unapproved"}
        )
        with patch("attendance.util.scouting.util.get_current_season", return_value=season):
            end_meeting(meeting.id)
        meeting.refresh_from_db()
        assert meeting.ended is True

    def test_get_attendance_with_meeting_id(self, test_user):
        """Line 250: get_attendance filtered by meeting_id."""
        from attendance.util import get_attendance
        from attendance.models import Meeting, MeetingType, Attendance, AttendanceApprovalType
        from scouting.models import Season
        season = Season.objects.create(season="2024gam", current="y", game="G", manual="")
        mt, _ = MeetingType.objects.get_or_create(
            meeting_typ="reggam", defaults={"meeting_nm": "Regular GAM"}
        )
        now = datetime.datetime.now(pytz.UTC)
        meeting = Meeting.objects.create(
            season=season, meeting_typ=mt, title="GAM",
            description="", start=now, end=now + datetime.timedelta(hours=1)
        )
        approval, _ = AttendanceApprovalType.objects.get_or_create(
            approval_typ="appgam", defaults={"approval_nm": "Approved GAM"}
        )
        Attendance.objects.create(
            user=test_user, meeting=meeting, season=season,
            time_in=now, time_out=now + datetime.timedelta(hours=1),
            absent=False, approval_typ=approval
        )
        with patch("attendance.util.scouting.util.get_current_season", return_value=season):
            result = get_attendance(test_user.id, meeting_id=meeting.id)
        assert len(result) >= 1
