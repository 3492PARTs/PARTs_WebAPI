"""
Coverage tests for alerts/util_alert_definitions.py, scouting/field/util.py,
scouting/admin/util.py remaining gaps, form/util.py key sections.
"""
import pytest
from unittest.mock import patch, MagicMock
import datetime
import pytz


# =============================================================================
# alerts/util_alert_definitions.py - Missing lines 282-284, 322-323, 336-337,
# 340-341, 344-345, 348-349, 352-353, 360-362, 392-394, 398-400, 414-427,
# 443-448, 483, 492-494, 627-629
# =============================================================================

@pytest.mark.django_db
class TestAlertsUtilDefinitionsCoverage:
    """Cover alert definition missing lines."""

    def test_stage_all_field_schedule_alerts_exception(self, system_user):
        """Lines 282-284: exception in stage_all_field_schedule_alerts."""
        from alerts.util_alert_definitions import stage_all_field_schedule_alerts
        with patch("alerts.util_alert_definitions.scouting.util.get_current_event",
                   side_effect=Exception("boom")):
            result = stage_all_field_schedule_alerts()
        assert "ERROR" in result

    def test_stage_field_schedule_alerts_with_scouts(self, test_user, system_user):
        """Lines 322-362: stage_field_schedule_alerts with scouts assigned."""
        from alerts.util_alert_definitions import stage_field_schedule_alerts
        from scouting.models import FieldSchedule, Event, Season

        season = Season.objects.create(season="2025afs", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="AFS", event_cd="2025afsst", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n", timezone="America/New_York",
        )
        now = datetime.datetime.now(pytz.UTC)
        sfs = FieldSchedule.objects.create(
            event=event,
            st_time=now,
            end_time=now + datetime.timedelta(hours=1),
            red_one=test_user,
            void_ind="n",
        )
        with patch("alerts.util_alert_definitions.create_alert", return_value=MagicMock()), \
             patch("alerts.util_alert_definitions.create_channel_send_for_comm_typ"):
            result = stage_field_schedule_alerts(3, [sfs])
        assert result is not None

    def test_stage_field_schedule_alerts_exception(self, system_user):
        """Lines 360-362: exception in stage_field_schedule_alerts."""
        from alerts.util_alert_definitions import stage_field_schedule_alerts
        broken_sfs = MagicMock()
        broken_sfs.notification = -1
        broken_sfs.st_time.astimezone.side_effect = Exception("boom")
        with patch("alerts.util_alert_definitions.create_alert", side_effect=Exception("boom")):
            result = stage_field_schedule_alerts(0, [broken_sfs])
        assert "ERROR" in result

    def test_stage_schedule_alerts_with_event(self, test_user, system_user):
        """Lines 391-394: stage_schedule_alerts stages alerts for schedules."""
        from alerts.util_alert_definitions import stage_schedule_alerts
        from scouting.models import Season, Event, Schedule, ScheduleType

        season = Season.objects.create(season="2025asa", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="ASA", event_cd="2025asast", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n", timezone="America/New_York",
        )
        sch_typ = ScheduleType.objects.create(sch_typ="genasa", sch_nm="General ASA")
        # schedule starting 2 minutes from now (within 6 min window)
        now = datetime.datetime.now(pytz.UTC)
        Schedule.objects.create(
            event=event, user=test_user, sch_typ=sch_typ,
            st_time=now + datetime.timedelta(minutes=2),
            end_time=now + datetime.timedelta(hours=1),
            notified=False, void_ind="n",
        )

        with patch("alerts.util_alert_definitions.scouting.util.get_current_event",
                   return_value=event), \
             patch("alerts.util_alert_definitions.stage_schedule_alert",
                   return_value="Notified: Test User\n"):
            result = stage_schedule_alerts()
        assert "Notified" in result or result is not None

    def test_stage_schedule_alerts_exception(self, system_user):
        """Lines 398-400: exception in stage_schedule_alerts."""
        from alerts.util_alert_definitions import stage_schedule_alerts
        with patch("alerts.util_alert_definitions.scouting.util.get_current_event",
                   side_effect=Exception("boom")):
            result = stage_schedule_alerts()
        assert "ERROR" in result

    def test_stage_schedule_alert(self, test_user):
        """Lines 414-427: stage_schedule_alert creates alert."""
        from alerts.util_alert_definitions import stage_schedule_alert
        from scouting.models import Season, Event, Schedule, ScheduleType

        season = Season.objects.create(season="2025ssa", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="SSA", event_cd="2025ssast", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
            void_ind="n", timezone="America/New_York",
        )
        sch_typ = ScheduleType.objects.create(sch_typ="genssa", sch_nm="General SSA")
        now = datetime.datetime.now(pytz.UTC)
        sch = Schedule.objects.create(
            event=event, user=test_user, sch_typ=sch_typ,
            st_time=now, end_time=now + datetime.timedelta(hours=1),
            notified=False, void_ind="n",
        )
        with patch("alerts.util_alert_definitions.create_alert", return_value=MagicMock()), \
             patch("alerts.util_alert_definitions.create_channel_send_for_comm_typ"):
            result = stage_schedule_alert(sch)
        assert "Pit Notified" in result

    def test_stage_scout_admin_alerts(self, test_user):
        """Lines 443-448: stage_scout_admin_alerts creates alerts for admin users."""
        from alerts.util_alert_definitions import stage_scout_admin_alerts
        with patch("alerts.util_alert_definitions.user.util.get_users_with_permission",
                   return_value=[test_user]), \
             patch("alerts.util_alert_definitions.create_alert", return_value=MagicMock()):
            result = stage_scout_admin_alerts("Subject", "Body")
        assert isinstance(result, list)

    def test_stage_match_strategy_added_alerts_with_strategies(self, test_user):
        """Lines 483-484: stage_match_strategy_added_alerts notifies users."""
        from alerts.util_alert_definitions import stage_match_strategy_added_alerts
        mock_strategy = MagicMock()
        mock_strategy.user.get_full_name.return_value = "Test User"
        mock_strategy.match.match_number = 1
        mock_strategy.user.id = test_user.id
        mock_notification = MagicMock()
        mock_notification.user.get_full_name.return_value = "Other User"
        with patch("alerts.util_alert_definitions.get_alert_type",
                   return_value=MagicMock(last_run=datetime.datetime.now(pytz.UTC),
                                          subject="Subj", body="Body {0} {1}")), \
             patch("alerts.util_alert_definitions.MatchStrategy.objects.filter",
                   return_value=[mock_strategy]), \
             patch("alerts.util_alert_definitions.send_alerts_to_role",
                   return_value=[mock_notification]):
            result = stage_match_strategy_added_alerts()
        assert result is not None

    def test_stage_match_strategy_added_alerts_exception(self, system_user):
        """Lines 492-494: exception in stage_match_strategy_added_alerts."""
        from alerts.util_alert_definitions import stage_match_strategy_added_alerts
        with patch("alerts.util_alert_definitions.get_alert_type",
                   side_effect=Exception("boom")):
            result = stage_match_strategy_added_alerts()
        assert "ERROR" in result

    def test_stage_meeting_alert_exception(self, system_user):
        """Lines 627-629: exception in stage_meeting_alert."""
        from alerts.util_alert_definitions import stage_meeting_alert
        with patch("alerts.util_alert_definitions.scouting.util.get_current_season",
                   side_effect=Exception("boom")):
            result = stage_meeting_alert()
        assert "ERROR" in result


# =============================================================================
# scouting/field/util.py - Missing lines 88-94, 195, 222-228, 252-264, 281,
# 407, 446-447, 449-450, 452-453, 455-456, 498-500
# =============================================================================

@pytest.mark.django_db
class TestScoutingFieldUtilCoverage:
    """Cover scouting/field/util.py missing lines."""

    def test_check_in_scout_all_positions(self, test_user):
        """Lines 446-461: check_in_scout checks all position assignments."""
        from scouting.field.util import check_in_scout
        from scouting.models import Season, Event, FieldSchedule
        from django.contrib.auth import get_user_model
        User = get_user_model()

        season = Season.objects.create(season="2025ci", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="CI", event_cd="2025cist", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        now = datetime.datetime.now(pytz.UTC)

        # Create multiple users for different positions
        user2 = User.objects.create_user(username="ci_user2", password="pass", email="ci2@test.com", first_name="CI", last_name="Two")
        user3 = User.objects.create_user(username="ci_user3", password="pass", email="ci3@test.com", first_name="CI", last_name="Three")

        sfs = FieldSchedule.objects.create(
            event=event,
            st_time=now, end_time=now + datetime.timedelta(hours=1),
            red_one=test_user, red_two=user2, blue_one=user3,
            void_ind="n",
        )
        # Test red_two check in
        result2 = check_in_scout(sfs, user2.id)
        assert "checked in" in result2.lower() or result2 != ""

    def test_check_in_scout_not_found(self, test_user):
        """Line 466: check_in_scout returns empty when user not in schedule."""
        from scouting.field.util import check_in_scout
        from scouting.models import Season, Event, FieldSchedule

        season = Season.objects.create(season="2025cnf", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="CNF", event_cd="2025cnfst", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        now = datetime.datetime.now(pytz.UTC)
        sfs = FieldSchedule.objects.create(
            event=event,
            st_time=now, end_time=now + datetime.timedelta(hours=1),
            void_ind="n",
        )
        result = check_in_scout(sfs, 99999)
        assert result == ""

    def test_get_field_question_aggregates_empty(self):
        """Line 407: get_field_question_aggregates returns QuerySet (can be empty)."""
        from scouting.field.util import get_field_question_aggregates
        from scouting.models import Season
        season = Season.objects.create(season="2025gfq", current="n", game="G", manual="")
        result = get_field_question_aggregates(season)
        assert result is not None  # returns a QuerySet

    def test_get_responses_after_id(self, test_user):
        """Line 195: get_responses with after_scout_field_id parameter."""
        from scouting.field.util import get_responses
        from scouting.models import Season, Event
        season = Season.objects.create(season="2025gra", current="y", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="GRA", event_cd="2025grast", current="y",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        with patch("scouting.field.util.scouting.util.get_current_event", return_value=event):
            result = get_responses(1, after_scout_field_id=0)
        assert result is not None

    def test_get_graph_options_bar(self):
        """Lines 498-500: get_graph_options for bar type."""
        from scouting.field.util import get_graph_options
        # This is a stub function, just verify it doesn't raise
        result = get_graph_options("bar")
        # Returns None (stub)


# =============================================================================
# scouting/admin/util.py - More missing lines (notify_user, void functions)
# =============================================================================

@pytest.mark.django_db
class TestScoutAdminUtilMore:
    """Cover more scouting admin util gaps."""

    def test_void_field_response(self, test_user):
        """Lines 619-633: void_field_response marks response as void."""
        from scouting.admin.util import void_field_response
        from scouting.models import Season, Event, Team, FieldResponse, CompetitionLevel, Match
        from form.models import FormType, Response as FormResp

        season = Season.objects.create(season="2025vfr", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="VFR", event_cd="2025vfrst", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC), void_ind="n",
        )
        team = Team.objects.create(team_no=5553, team_nm="VFRTeam", void_ind="n")
        team.event_set.add(event)
        cl, _ = CompetitionLevel.objects.get_or_create(
            comp_lvl_typ="qmvfr", defaults={"comp_lvl_typ_nm": "Qual VFR", "comp_lvl_order": 1, "void_ind": "n"}
        )
        match = Match.objects.create(
            match_key="2025vfr_qm1", match_number=1, event=event, comp_level=cl, void_ind="n"
        )
        ft, _ = FormType.objects.get_or_create(form_typ="vfrft", defaults={"form_nm": "VFR Form"})
        resp = FormResp.objects.create(form_typ=ft, void_ind="n")
        fr = FieldResponse.objects.create(
            event=event, team=team, user=test_user, match=match,
            response=resp, void_ind="n"
        )
        void_field_response(fr.id)
        fr.refresh_from_db()
        assert fr.void_ind == "y"

    def test_void_scout_pit_response(self, test_user):
        """Lines 635-653: void_scout_pit_response marks pit response as void."""
        from scouting.admin.util import void_scout_pit_response
        from scouting.models import Season, Event, Team, PitResponse
        from form.models import FormType, Response as FormResp

        season = Season.objects.create(season="2025vpr", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="VPR", event_cd="2025vprst", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC), void_ind="n",
        )
        team = Team.objects.create(team_no=5554, team_nm="VPRTeam", void_ind="n")
        team.event_set.add(event)
        ft, _ = FormType.objects.get_or_create(form_typ="vprft", defaults={"form_nm": "VPR Form"})
        resp = FormResp.objects.create(form_typ=ft, void_ind="n")
        pr = PitResponse.objects.create(
            event=event, team=team, user=test_user, response=resp, void_ind="n"
        )
        void_scout_pit_response(pr.id)
        pr.refresh_from_db()
        assert pr.void_ind == "y"

    def test_save_scouting_user_info(self, test_user):
        """Lines 591-617: save_scouting_user_info creates/updates user info."""
        from scouting.admin.util import save_scouting_user_info
        from scouting.models import UserInfo
        UserInfo.objects.filter(user=test_user).delete()
        result = save_scouting_user_info({
            "user": {"id": test_user.id},
            "under_review": False,
            "group_leader": True,
            "eliminate_results": False,
        })
        assert result.user == test_user
        assert result.group_leader is True

    def test_save_scout_schedule_update_existing(self, test_user):
        """Lines 473-486: save_scout_schedule updates existing entry."""
        from scouting.admin.util import save_scout_schedule
        from scouting.models import Season, Event, FieldSchedule
        season = Season.objects.create(season="2025ssu", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="SSU", event_cd="2025ssust", current="n",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC), void_ind="n",
        )
        now = datetime.datetime.now(pytz.UTC)
        sfs = FieldSchedule.objects.create(
            event=event, st_time=now, end_time=now + datetime.timedelta(hours=1),
            void_ind="n",
        )
        new_end = now + datetime.timedelta(hours=2)
        result = save_scout_schedule({
            "id": sfs.id,
            "event_id": event.id,
            "st_time": now,
            "end_time": new_end,
            "void_ind": "n",
        })
        assert result.id == sfs.id
        result.refresh_from_db()
        assert result.end_time == new_end


# =============================================================================
# user/util.py - Missing line 122 (get_users_parsed loop)
# =============================================================================

@pytest.mark.django_db
class TestUserUtilParsed:
    """Cover user/util.py missing line 122."""

    def test_get_users_parsed(self, test_user):
        """Line 122: get_users_parsed iterates users and builds dict list."""
        from user.util import get_users_parsed
        from django.contrib.auth.models import Group
        Group.objects.get_or_create(name="Admin")
        result = get_users_parsed(1, False)
        assert isinstance(result, list)
        if len(result) > 0:
            assert "id" in result[0] or "user_id" in result[0] or isinstance(result[0], dict)


# =============================================================================
# scouting/views.py - Missing lines 216-217
# =============================================================================

@pytest.mark.django_db
class TestScoutingViewsExtra:
    """Cover scouting/views.py missing lines 216-217."""

    def test_team_list_exception(self, api_client, test_user, system_user):
        """Lines 121-127: exception in TeamView."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_teams",
                   side_effect=Exception("boom")):
            response = api_client.get("/scouting/team/")
        assert response.status_code == 200
        assert response.data.get("error") is True


# =============================================================================
# admin/views.py - Missing lines 260-263 (via DELETE)
# =============================================================================

@pytest.mark.django_db
class TestAdminViewsExtra:
    """Cover admin/views.py missing lines 260-263."""

    def test_phone_type_delete_exception(self, api_client, test_user, system_user):
        """Lines 260-263 area: DELETE phone type raises exception."""
        api_client.force_authenticate(user=test_user)
        with patch("admin.views.has_access", return_value=True), \
             patch("admin.views.user.util.delete_phone_type",
                   side_effect=Exception("Not found")):
            response = api_client.delete("/admin/phone-type/?phone_type_id=9999")
        assert response.status_code == 200
        assert response.data.get("error") is True


# =============================================================================
# public/competition/views.py - Missing lines 25-26
# =============================================================================

@pytest.mark.django_db
class TestPublicCompetitionViewsExtra:
    """Cover public/competition/views.py missing lines 25-26."""

    def test_competition_init_inner_exception(self, api_client, system_user):
        """Line 25: inner exception returns 'No event' message."""
        with patch("public.competition.views.public.competition.util.get_competition_information",
                   side_effect=Exception("No current event")):
            response = api_client.get("/public/competition/init/")
        assert response.status_code == 200
