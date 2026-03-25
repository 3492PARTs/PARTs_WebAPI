"""
Coverage tests for remaining gaps:
- scouting/field/views.py (81% → higher)
- attendance/util.py (86% → higher)
- attendance/models.py (98% → 100%)
- form/models.py (97% → 100%)
"""
import pytest
from unittest.mock import patch, MagicMock
import datetime
import pytz


# =============================================================================
# scouting/field/views.py - Missing lines 40, 71-78, 86-87, 117, 150-153, 164-165, 188-192
# =============================================================================

@pytest.mark.django_db
class TestScoutingFieldFormView:
    """FormView coverage."""

    def test_get_success(self, api_client, test_user):
        """Line 40: FormView GET success."""
        api_client.force_authenticate(user=test_user)
        mock_data = {"id": 1, "season_id": 1, "img_url": None}
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.field.util.get_field_form", return_value=mock_data), \
             patch("scouting.field.views.FieldFormFormSerializer") as mock_ser:
            mock_ser.return_value.data = mock_data
            response = api_client.get("/scouting/field/form/")
        assert response.status_code == 200

    def test_get_access_denied(self, api_client, test_user):
        """Lines 42-48: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=False):
            response = api_client.get("/scouting/field/form/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user):
        """Lines 50-56: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.field.util.get_field_form",
                   side_effect=Exception("boom")):
            response = api_client.get("/scouting/field/form/")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutingFieldResponseColumnsView:
    """ResponseColumnsView coverage."""

    def test_get_success(self, api_client, test_user):
        """Lines 71-78: success path."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.field.util.get_field_question_aggregates",
                   return_value=[]), \
             patch("scouting.field.views.scouting.util.get_current_season",
                   return_value=MagicMock()), \
             patch("scouting.field.views.scouting.field.util.get_table_columns",
                   return_value=[]):
            response = api_client.get("/scouting/field/response-columns/")
        assert response.status_code == 200

    def test_get_access_denied(self, api_client, test_user):
        """Lines 80-85: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=False):
            response = api_client.get("/scouting/field/response-columns/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user):
        """Lines 86-93: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.util.get_current_season",
                   side_effect=Exception("boom")):
            response = api_client.get("/scouting/field/response-columns/")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutingFieldResponsesView:
    """ResponsesView coverage."""

    def test_get_response_instance(self, api_client, test_user):
        """Line 117: when get_responses returns a Response object."""
        from rest_framework.response import Response as DRFResponse
        api_client.force_authenticate(user=test_user)
        mock_resp = DRFResponse(data={"test": True})
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.field.util.get_responses",
                   return_value=mock_resp):
            response = api_client.get("/scouting/field/responses/")
        assert response.status_code == 200

    def test_get_access_denied(self, api_client, test_user):
        """Lines 122-127: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=False):
            response = api_client.get("/scouting/field/responses/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user):
        """Lines 128-135: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.field.util.get_responses",
                   side_effect=Exception("boom")):
            response = api_client.get("/scouting/field/responses/")
        assert response.status_code == 200
        assert response.data.get("error") is True


@pytest.mark.django_db
class TestScoutingFieldCheckInView:
    """CheckInView coverage."""

    def test_get_success(self, api_client, test_user):
        """Lines 150-155: check in success."""
        api_client.force_authenticate(user=test_user)
        mock_sfs = MagicMock()
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.util.get_scout_field_schedule",
                   return_value=mock_sfs), \
             patch("scouting.field.views.scouting.field.util.check_in_scout",
                   return_value="Checked in"):
            response = api_client.get("/scouting/field/check-in/?scout_field_sch_id=1")
        assert response.status_code == 200

    def test_get_access_denied(self, api_client, test_user):
        """Lines 157-162: access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=False):
            response = api_client.get("/scouting/field/check-in/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_exception(self, api_client, test_user):
        """Lines 164-171: exception."""
        api_client.force_authenticate(user=test_user)
        with patch("scouting.field.views.has_access", return_value=True), \
             patch("scouting.field.views.scouting.util.get_scout_field_schedule",
                   side_effect=Exception("boom")):
            response = api_client.get("/scouting/field/check-in/?scout_field_sch_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True


# =============================================================================
# attendance/models.py - Missing line 82 (duration_hours with no time_out)
# =============================================================================

@pytest.mark.django_db
class TestAttendanceModelMethods:
    """Cover attendance model missing lines."""

    def test_duration_hours_no_timeout(self, test_user):
        """Line 82: duration_hours returns 0 when time_out is None."""
        from attendance.models import Attendance, AttendanceApprovalType, Meeting, MeetingType
        from scouting.models import Season
        season = Season.objects.create(season="2024dur", current="n", game="G", manual="")
        mt = MeetingType.objects.create(meeting_typ="regdur", meeting_nm="Regular Dur")
        now = datetime.datetime.now(pytz.UTC)
        meeting = Meeting.objects.create(
            season=season, meeting_typ=mt, title="Test Meeting",
            description="desc", start=now, end=now + datetime.timedelta(hours=1),
            ended=False
        )
        approval = AttendanceApprovalType.objects.create(
            approval_typ="unappdur", approval_nm="Unapproved Dur"
        )
        att = Attendance.objects.create(
            user=test_user, meeting=meeting, season=season,
            time_in=now, time_out=None,
            absent=False, approval_typ=approval
        )
        assert att.duration_hours() == 0


# =============================================================================
# attendance/util.py - Missing lines 29, 106, 117, 144, 163, 168, 173-176, 250, 279-297
# =============================================================================

@pytest.mark.django_db
class TestAttendanceUtilCoverage:
    """Cover attendance util missing lines."""

    def test_get_meetings_by_id(self):
        """Line 29: get single meeting by id."""
        from attendance.util import get_meetings
        from attendance.models import Meeting, MeetingType
        from scouting.models import Season
        season = Season.objects.create(season="2024gm", current="n", game="G", manual="")
        mt = MeetingType.objects.create(meeting_typ="reggm", meeting_nm="Regular GM")
        now = datetime.datetime.now(pytz.UTC)
        mtg = Meeting.objects.create(
            season=season, meeting_typ=mt, title="Test",
            description="", start=now, end=now + datetime.timedelta(hours=1)
        )
        result = get_meetings(id=mtg.id)
        assert result.id == mtg.id

    def test_get_meeting_hours_with_meeting_types(self):
        """Lines 106, 117: meeting_hours with reg/evnt/bns types."""
        from attendance.util import get_meeting_hours
        from attendance.models import Meeting, MeetingType
        from scouting.models import Season
        season = Season.objects.create(season="2024mh", current="y", game="G", manual="")
        now = datetime.datetime.now(pytz.UTC)

        for typ, nm in [("reg", "Regular"), ("evnt", "Event"), ("bns", "Bonus")]:
            mt, _ = MeetingType.objects.get_or_create(
                meeting_typ=typ, defaults={"meeting_nm": nm}
            )
            Meeting.objects.create(
                season=season, meeting_typ=mt, title=f"T {typ}",
                description="", start=now, end=now + datetime.timedelta(hours=2),
                ended=True
            )

        result = get_meeting_hours()
        assert "hours" in result
        assert "event_hours" in result
        assert "bonus_hours" in result

    def test_get_meeting_hours_future_meeting(self):
        """Line 115: meeting not ended (total_future branch)."""
        from attendance.util import get_meeting_hours
        from attendance.models import Meeting, MeetingType
        from scouting.models import Season
        season = Season.objects.create(season="2024mhf", current="y", game="G", manual="")
        now = datetime.datetime.now(pytz.UTC)
        mt, _ = MeetingType.objects.get_or_create(
            meeting_typ="reg", defaults={"meeting_nm": "Regular"}
        )
        Meeting.objects.create(
            season=season, meeting_typ=mt, title="Future",
            description="", start=now, end=now + datetime.timedelta(hours=2),
            ended=False  # not ended = future
        )
        result = get_meeting_hours()
        assert result["hours_future"] >= 0

    def test_get_attendance_report_with_user(self, test_user):
        """Line 144: get_attendance_report for specific user_id."""
        from attendance.util import get_attendance_report
        from scouting.models import Season
        Season.objects.create(season="2024gar", current="y", game="G", manual="")
        result = get_attendance_report(user_id=test_user.id)
        assert isinstance(result, list)

    def test_get_attendance_report_all_users(self, test_user):
        """Line 146: get_attendance_report for all users."""
        from attendance.util import get_attendance_report
        from scouting.models import Season
        Season.objects.create(season="2024gara", current="y", game="G", manual="")
        result = get_attendance_report()
        assert isinstance(result, list)

    def test_get_attendance_report_attendance_branches(self, test_user):
        """Lines 163, 168, 173-176: attendance report with approved attendance."""
        from attendance.util import get_attendance_report
        from attendance.models import Meeting, MeetingType, Attendance, AttendanceApprovalType
        from scouting.models import Season
        season = Season.objects.create(season="2024garb", current="y", game="G", manual="")
        now = datetime.datetime.now(pytz.UTC)
        mt, _ = MeetingType.objects.get_or_create(
            meeting_typ="reg", defaults={"meeting_nm": "Regular"}
        )
        mtg = Meeting.objects.create(
            season=season, meeting_typ=mt, title="T",
            description="", start=now, end=now + datetime.timedelta(hours=2),
            ended=True
        )
        approval_app, _ = AttendanceApprovalType.objects.get_or_create(
            approval_typ="app", defaults={"approval_nm": "Approved"}
        )
        # Create approved attendance with time_out
        Attendance.objects.create(
            user=test_user, meeting=mtg, season=season,
            time_in=now, time_out=now + datetime.timedelta(hours=2),
            absent=False, approval_typ=approval_app
        )
        with patch("attendance.util.scouting.util.get_current_season", return_value=season):
            result = get_attendance_report(user_id=test_user.id)
        assert isinstance(result, list)

    def test_get_attendance_report_bns_evnt_meeting_types(self, test_user):
        """Lines 173-176: attendance report with bns and evnt meeting types."""
        from attendance.util import get_attendance_report
        from attendance.models import Meeting, MeetingType, Attendance, AttendanceApprovalType
        from scouting.models import Season
        season = Season.objects.create(season="2024garbc", current="y", game="G", manual="")
        now = datetime.datetime.now(pytz.UTC)
        approval_app, _ = AttendanceApprovalType.objects.get_or_create(
            approval_typ="app", defaults={"approval_nm": "Approved"}
        )
        for typ, nm in [("bns", "Bonus"), ("evnt", "Event")]:
            mt, _ = MeetingType.objects.get_or_create(
                meeting_typ=typ, defaults={"meeting_nm": nm}
            )
            mtg = Meeting.objects.create(
                season=season, meeting_typ=mt, title=f"T {typ}",
                description="", start=now, end=now + datetime.timedelta(hours=1),
                ended=True
            )
            Attendance.objects.create(
                user=test_user, meeting=mtg, season=season,
                time_in=now, time_out=now + datetime.timedelta(hours=1),
                absent=False, approval_typ=approval_app
            )
        with patch("attendance.util.scouting.util.get_current_season", return_value=season):
            result = get_attendance_report(user_id=test_user.id)
        assert isinstance(result, list)


# =============================================================================
# form/models.py - Missing __str__ lines 178, 216, 225, 237, 291, 304
# =============================================================================

@pytest.mark.django_db
class TestFormModelsRemainingStr:
    """Cover remaining form model __str__ methods."""

    def test_flow_answer_str(self):
        """Line 216: FlowAnswer.__str__."""
        from form.models import FlowAnswer, Question, QuestionType, FormType, Flow, Answer, Response
        ft, _ = FormType.objects.get_or_create(
            form_typ="flwans", defaults={"form_nm": "FlowAns"}
        )
        qt, _ = QuestionType.objects.get_or_create(
            question_typ="txtfa", defaults={"question_typ_nm": "TxtFA", "void_ind": "n", "is_list": False}
        )
        q = Question.objects.create(
            question="FA Q?", order=1, question_typ=qt, form_typ=ft,
            void_ind="n", table_col_width="100", required="n"
        )
        flow = Flow.objects.create(name="FA Flow", form_typ=ft, void_ind="n")
        resp = Response.objects.create(form_typ=ft, void_ind="n")
        ans = Answer.objects.create(question=q, response=resp, value="x", void_ind="n")
        fa = FlowAnswer.objects.create(answer=ans, question=q, value="flow_val", void_ind="n")
        result = str(fa)
        assert "flow_val" in result

    def test_graph_question_type_str(self):
        """Line 225: GraphQuestionType.__str__."""
        from form.models import GraphQuestionType
        gqt = GraphQuestionType.objects.create(
            graph_question_typ="gqtst", graph_question_nm="GQT Str", void_ind="n"
        )
        result = str(gqt)
        assert "gqtst" in result

    def test_graph_type_str(self):
        """Line 237: GraphType.__str__."""
        from form.models import GraphType
        gt = GraphType.objects.create(
            graph_typ="gtst2", graph_nm="GT Str2", void_ind="n"
        )
        result = str(gt)
        assert "gtst2" in result

    def test_graph_category_attribute_str(self, test_user):
        """Line 291: GraphCategoryAttribute.__str__."""
        from form.models import (
            Graph, GraphType, GraphCategory, GraphCategoryAttribute,
            QuestionConditionType, FormType, QuestionType, Question
        )
        gt = GraphType.objects.create(graph_typ="gtca", graph_nm="GT CA", void_ind="n")
        g = Graph.objects.create(
            graph_typ=gt, name="CA Graph",
            x_scale_min=0, x_scale_max=100,
            y_scale_min=0, y_scale_max=100,
            active="y", void_ind="n", creator=test_user
        )
        gc = GraphCategory.objects.create(graph=g, category="ca_cat", order=1, void_ind="n")
        qct = QuestionConditionType.objects.create(
            question_condition_typ="eqca", question_condition_nm="Equal CA", void_ind="n"
        )
        gca = GraphCategoryAttribute.objects.create(
            graph_category=gc, question_condition_typ=qct,
            value="attr_val", void_ind="n"
        )
        result = str(gca)
        assert "attr_val" in result

    def test_graph_question_str(self, test_user):
        """Line 304: GraphQuestion.__str__."""
        from form.models import Graph, GraphType, GraphQuestion
        gt = GraphType.objects.create(graph_typ="gtgq", graph_nm="GT GQ", void_ind="n")
        g = Graph.objects.create(
            graph_typ=gt, name="GQ Graph",
            x_scale_min=0, x_scale_max=100,
            y_scale_min=0, y_scale_max=100,
            active="y", void_ind="n", creator=test_user
        )
        gq = GraphQuestion.objects.create(graph=g, active="y", void_ind="n")
        result = str(gq)
        assert str(gq.id) in result

    def test_question_aggregate_question_str(self):
        """Line 178: QuestionAggregateQuestion.__str__."""
        from form.models import (
            QuestionAggregateQuestion, QuestionAggregate, QuestionAggregateType,
            Question, QuestionType, FormType
        )
        ft, _ = FormType.objects.get_or_create(
            form_typ="qaqt", defaults={"form_nm": "QAQ Form"}
        )
        qt, _ = QuestionType.objects.get_or_create(
            question_typ="txtqaq", defaults={"question_typ_nm": "TxtQAQ", "void_ind": "n", "is_list": False}
        )
        q = Question.objects.create(
            question="QAQ Q?", order=1, question_typ=qt, form_typ=ft,
            void_ind="n", table_col_width="100", required="n"
        )
        qat = QuestionAggregateType.objects.create(
            question_aggregate_typ="sumqaq", question_aggregate_nm="Sum QAQ", void_ind="n"
        )
        qa = QuestionAggregate.objects.create(
            question_aggregate_typ=qat, name="Test Agg QAQ", void_ind="n"
        )
        qaq = QuestionAggregateQuestion.objects.create(
            question_aggregate=qa, question=q, void_ind="n"
        )
        result = str(qaq)
        assert str(qaq.id) in result


# =============================================================================
# scouting/models.py - Missing __str__ lines 163, 185, 231, 267, 279, 291, 303, 315, 329, 341, 349, 361, 378, 390
# =============================================================================

@pytest.mark.django_db
class TestScoutingModelsRemainingStr:
    """Cover remaining scouting model __str__ methods."""

    def test_pit_response_str(self, test_user):
        """Line 163: PitResponse.__str__."""
        from scouting.models import PitResponse, Event, Season, Team
        from form.models import Response as FormResponse, FormType
        season = Season.objects.create(season="2027pr", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="PR", event_cd="2027prst",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        team = Team.objects.create(team_no=8886, team_nm="PitTeamStr", void_ind="n")
        team.event_set.add(event)
        ft, _ = FormType.objects.get_or_create(
            form_typ="pitst", defaults={"form_nm": "Pit Form Str"}
        )
        form_resp = FormResponse.objects.create(form_typ=ft, void_ind="n")
        pr = PitResponse.objects.create(
            response=form_resp, event=event, team=team, user=test_user, void_ind="n"
        )
        result = str(pr)
        assert str(pr.id) in result

    def test_pit_image_str(self, test_user):
        """Line 185: PitImage.__str__."""
        from scouting.models import PitImage, PitResponse, PitImageType, Event, Season, Team
        from form.models import Response as FormResponse, FormType
        season = Season.objects.create(season="2027pi", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="PI", event_cd="2027pist",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        team = Team.objects.create(team_no=8884, team_nm="PitImgTeam", void_ind="n")
        team.event_set.add(event)
        pit_type, _ = PitImageType.objects.get_or_create(
            pit_image_typ="sidest", defaults={"pit_image_nm": "Side Str"}
        )
        ft, _ = FormType.objects.get_or_create(
            form_typ="piist", defaults={"form_nm": "PII Form Str"}
        )
        form_resp = FormResponse.objects.create(form_typ=ft, void_ind="n")
        pr = PitResponse.objects.create(
            response=form_resp, event=event, team=team, user=test_user, void_ind="n"
        )
        img = PitImage.objects.create(
            pit_response=pr, pit_image_typ=pit_type, void_ind="n"
        )
        result = str(img)
        assert str(img.id) in result

    def test_user_info_str(self, test_user):
        """Line 231: UserInfo.__str__."""
        from scouting.models import UserInfo
        ui = UserInfo.objects.create(
            user=test_user, under_review=False, group_leader=False
        )
        result = str(ui)
        assert str(ui.id) in result

    def test_team_note_str(self, test_user):
        """Line 267: TeamNote.__str__."""
        from scouting.models import TeamNote, Event, Season, Team
        season = Season.objects.create(season="2028tnst", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="TN", event_cd="2028tnst",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        team = Team.objects.create(team_no=7770, team_nm="TNTeam", void_ind="n")
        team.event_set.add(event)
        tn = TeamNote.objects.create(
            event=event, team=team, user=test_user, note="Test note", void_ind="n"
        )
        result = str(tn)
        assert str(tn.id) in result
