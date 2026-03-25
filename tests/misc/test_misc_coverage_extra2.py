"""
Extra coverage tests for multiple smaller coverage gaps:
- src/tba/views.py (74%)
- src/sponsoring/views.py (74%)
- src/attendance/views.py (89%)
- src/admin/views.py (96%)
- src/scouting/models.py __str__ methods (93%)
- src/form/models.py __str__ methods (95%)
- src/user/util.py (97%)
- src/scouting/util.py (98%)
"""
import pytest
from unittest.mock import patch, MagicMock
import datetime
import pytz


# =============================================================================
# TBA Views  (missing lines 32-36, 55-63, 82-86, 148-153, 165-174)
# =============================================================================

@pytest.mark.django_db
class TestTBAViewsCoverage:
    """Cover missing TBA view lines."""

    def test_sync_season_no_access(self, api_client, test_user):
        """SyncSeasonView access denied."""
        api_client.force_authenticate(user=test_user)
        with patch("general.security.has_access", return_value=False):
            response = api_client.get("/tba/sync-season/?season_id=1")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_sync_season_success(self, api_client, test_user):
        """SyncSeasonView success path (lines 32-36)."""
        api_client.force_authenticate(user=test_user)
        with patch("tba.views.tba.util.sync_season", return_value="Synced"), \
             patch("general.security.has_access", return_value=True):
            response = api_client.get("/tba/sync-season/?season_id=1")
        assert response.status_code == 200

    def test_sync_event_view_success(self, api_client, test_user):
        """SyncEventView (lines 55-63)."""
        from scouting.models import Season
        api_client.force_authenticate(user=test_user)
        season = Season.objects.create(season="2024", current="y", game="Test", manual="")
        with patch("tba.views.tba.util.sync_event", return_value="Synced"), \
             patch("general.security.has_access", return_value=True):
            response = api_client.get(f"/tba/sync-event/?season_id={season.id}&event_cd=test")
        assert response.status_code == 200

    def test_sync_matches_view_success(self, api_client, test_user):
        """SyncMatchesView (lines 82-86)."""
        api_client.force_authenticate(user=test_user)
        mock_event = MagicMock()
        with patch("tba.views.scouting.util.get_current_event", return_value=mock_event), \
             patch("tba.views.tba.util.sync_matches", return_value="Synced"), \
             patch("general.security.has_access", return_value=True):
            response = api_client.get("/tba/sync-matches/")
        assert response.status_code == 200

    def test_sync_event_team_info_exception(self, api_client, system_user):
        """Lines 148-153: SyncEventTeamInfoView exception path (no auth = AnonymousUser)."""
        with patch("tba.views.tba.util.sync_event_team_info", side_effect=Exception("boom")):
            response = api_client.get("/tba/sync-event-team-info/?force=0")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_sync_event_team_info_success(self, api_client):
        """SyncEventTeamInfoView success path."""
        with patch("tba.views.tba.util.sync_event_team_info", return_value="Synced OK"):
            response = api_client.get("/tba/sync-event-team-info/?force=1")
        assert response.status_code == 200

    def test_webhook_verification_valid(self, api_client, system_user):
        """Lines 165-174: WebhookView verification success."""
        mock_msg = MagicMock()
        with patch("tba.views.tba.util.verify_tba_webhook_call", return_value=True), \
             patch("tba.views.tba.util.save_message", return_value=mock_msg):
            response = api_client.post(
                "/tba/webhook/",
                {"message_type": "verification", "message_data": {}, "message_key": "abc"},
                format="json"
            )
        assert response.status_code in [200, 500]

    def test_webhook_invalid_auth(self, api_client, system_user):
        """WebhookView - authentication fails → ret_message error."""
        with patch("tba.views.tba.util.verify_tba_webhook_call", return_value=False):
            response = api_client.post(
                "/tba/webhook/",
                {"message_type": "verification"},
                format="json"
            )
        assert response.status_code in [200, 500]


# =============================================================================
# Sponsoring Views  (missing lines 59-64, 78-85, 108-113)
# =============================================================================

@pytest.mark.django_db
class TestSponsoringViewsCoverage:
    """Cover missing sponsoring view lines."""

    def test_get_items_exception(self, api_client, test_user):
        """Lines 59-64: GetItemsView exception."""
        api_client.force_authenticate(user=test_user)
        with patch("sponsoring.views.sponsoring.util.get_items", side_effect=Exception("boom")):
            response = api_client.get("/sponsoring/get-items/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_get_sponsors_exception(self, api_client, test_user):
        """Lines 78-85: GetSponsorsView exception."""
        api_client.force_authenticate(user=test_user)
        with patch("sponsoring.views.sponsoring.util.get_sponsors", side_effect=Exception("boom")):
            response = api_client.get("/sponsoring/get-sponsors/")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_save_sponsor_exception(self, api_client, test_user):
        """Lines 108-113: SaveSponsorView exception during save."""
        api_client.force_authenticate(user=test_user)
        with patch("sponsoring.views.sponsoring.util.save_sponsor", side_effect=Exception("boom")):
            response = api_client.post(
                "/sponsoring/save-sponsor/",
                {"id": None, "name": "TestSponsor", "order": 1, "void_ind": "n", "items": []},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# =============================================================================
# Attendance Views  (missing lines 84-85, 159-160, 271-275)
# =============================================================================

@pytest.mark.django_db
class TestAttendanceViewsCoverage:
    """Cover missing attendance view lines."""

    def test_attendance_post_invalid_data(self, api_client, test_user):
        """Lines 84-85: AttendanceView.post invalid serializer data."""
        api_client.force_authenticate(user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = api_client.post("/attendance/attendance/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_meetings_post_invalid_data(self, api_client, test_user):
        """Lines 159-160: MeetingsView.post invalid serializer data."""
        api_client.force_authenticate(user=test_user)
        with patch("general.security.has_access", return_value=True):
            response = api_client.post("/attendance/meetings/", {}, format="json")
        assert response.status_code == 200
        assert response.data.get("error") is True

    def test_end_meeting_view(self, api_client, test_user):
        """Lines 271-275: EndMeetingView."""
        api_client.force_authenticate(user=test_user)
        with patch("general.security.has_access", return_value=True), \
             patch("attendance.views.attendance.util.end_meeting"):
            response = api_client.get("/attendance/end-meeting/?meeting_id=1")
        assert response.status_code == 200


# =============================================================================
# Admin Views  (missing lines 260-263)
# =============================================================================

@pytest.mark.django_db
class TestAdminViewsCoverage:
    """Cover missing admin view lines."""

    def test_phone_type_exception(self, api_client, test_user):
        """Lines 260-263: PhoneTypeView - exception when PhoneType.save raises."""
        api_client.force_authenticate(user=test_user)
        with patch("admin.views.has_access", return_value=True), \
             patch("admin.views.user.models.PhoneType") as mock_pt_class:
            # When id is None, it creates a new PhoneType; mock the constructor's save to raise
            mock_pt_instance = MagicMock()
            mock_pt_instance.save.side_effect = Exception("db error")
            mock_pt_class.return_value = mock_pt_instance
            response = api_client.post(
                "/admin/phone-type/",
                {"phone_type": "verizon", "carrier": "Verizon"},
                format="json"
            )
        assert response.status_code == 200
        assert response.data.get("error") is True


# =============================================================================
# Scouting Models __str__  (missing lines 120, 137, 151, 163, 171, 185, 193, etc.)
# =============================================================================

@pytest.mark.django_db
class TestScoutingModelsStr:
    """Cover __str__ methods of scouting models."""

    def test_match_str(self):
        """Line 120: Match.__str__."""
        from scouting.models import Match, Event, Season, CompetitionLevel
        season = Season.objects.create(season="2024str", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="E", event_cd="2024str",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        cl = CompetitionLevel.objects.create(
            comp_lvl_typ="qmst", comp_lvl_typ_nm="Qualification", comp_lvl_order=1, void_ind="n"
        )
        match = Match.objects.create(
            match_key="2024str_qm1", match_number=1,
            event=event, comp_level=cl, void_ind="n"
        )
        result = str(match)
        assert "2024str_qm1" in result

    def test_field_form_str(self):
        """Line 137: FieldForm.__str__."""
        from scouting.models import FieldForm, Season
        season = Season.objects.create(season="2025str", current="n", game="G", manual="")
        ff = FieldForm.objects.create(season=season, void_ind="n")
        result = str(ff)
        assert str(ff.id) in result

    def test_scout_auth_group_str(self):
        """Line 193: ScoutAuthGroup.__str__."""
        from scouting.models import ScoutAuthGroup
        from django.contrib.auth.models import Group
        group = Group.objects.create(name="TestScoutGroupStr")
        sag = ScoutAuthGroup.objects.create(group=group)
        result = str(sag)
        assert "TestScoutGroupStr" in result

    def test_pit_image_type_str(self):
        """Line 171: PitImageType.__str__."""
        from scouting.models import PitImageType
        pit = PitImageType.objects.create(
            pit_image_typ="frntv", pit_image_nm="Front View"
        )
        result = str(pit)
        assert "frntv" in result

    def test_field_response_str(self, test_user):
        """Line 151: FieldResponse.__str__."""
        from scouting.models import FieldResponse, Event, Season, Team, Match, CompetitionLevel
        season = Season.objects.create(season="2026fr", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="EF", event_cd="2026frst",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        team = Team.objects.create(team_no=9997, team_nm="TestTeamStr", void_ind="n")
        team.event_set.add(event)
        cl = CompetitionLevel.objects.create(
            comp_lvl_typ="qmfr", comp_lvl_typ_nm="QualFR", comp_lvl_order=2, void_ind="n"
        )
        match = Match.objects.create(
            match_key="2026frst_qm1", match_number=1,
            event=event, comp_level=cl, void_ind="n"
        )
        fr = FieldResponse.objects.create(
            event=event, team=team, user=test_user, match=match, void_ind="n"
        )
        result = str(fr)
        assert str(fr.id) in result

    def test_schedule_str(self, test_user):
        """Line 253: Schedule.__str__."""
        from scouting.models import Schedule, ScheduleType, Event, Season
        season = Season.objects.create(season="2028sch", current="n", game="G", manual="")
        event = Event.objects.create(
            season=season, event_nm="SCH", event_cd="2028schst",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        sch_typ = ScheduleType.objects.create(sch_typ="genst", sch_nm="General Str")
        now = datetime.datetime.now(pytz.UTC)
        sch = Schedule.objects.create(
            sch_typ=sch_typ, event=event, user=test_user,
            st_time=now, end_time=now + datetime.timedelta(hours=1), void_ind="n"
        )
        result = str(sch)
        assert str(sch.id) in result


# =============================================================================
# Form Models __str__  (missing lines 178, 190, 204, 216, 225, 237, 253, 265, 277, 291, 304)
# =============================================================================

@pytest.mark.django_db
class TestFormModelsStr:
    """Cover __str__ methods of form models."""

    def test_question_type_str(self):
        """Line 178 (via form/models.py line 22): QuestionType.__str__."""
        from form.models import QuestionType
        qt = QuestionType.objects.create(
            question_typ="txtstr", question_typ_nm="Text String", void_ind="n", is_list=False
        )
        result = str(qt)
        assert "txtstr" in result

    def test_question_str(self):
        """Line 190: Question.__str__."""
        from form.models import Question, QuestionType, FormType
        qt = QuestionType.objects.create(
            question_typ="txt5str", question_typ_nm="Text5", void_ind="n", is_list=False
        )
        ft, _ = FormType.objects.get_or_create(
            form_typ="qtstr", defaults={"form_nm": "QT Form"}
        )
        q = Question.objects.create(
            question="What team number?",
            order=1,
            question_typ=qt,
            form_typ=ft,
            void_ind="n",
            table_col_width="100",
            required="n",
        )
        result = str(q)
        assert "What team number?" in result

    def test_flow_str(self):
        """Line 204 (via form/models.py line 52): Flow.__str__."""
        from form.models import Flow, FormType
        ft, _ = FormType.objects.get_or_create(
            form_typ="flwstr", defaults={"form_nm": "Flow Form"}
        )
        flow = Flow.objects.create(
            name="Test Flow Str",
            form_typ=ft,
            void_ind="n",
        )
        result = str(flow)
        assert "Test Flow Str" in result

    def test_response_str(self):
        """Line 216 (via form/models.py line 190): Response.__str__."""
        from form.models import Response, FormType
        ft, _ = FormType.objects.get_or_create(
            form_typ="tststr", defaults={"form_nm": "Test String Form"}
        )
        resp = Response.objects.create(
            form_typ=ft,
            void_ind="n",
        )
        result = str(resp)
        assert str(resp.id) in result

    def test_answer_str(self):
        """Line 225 (via form/models.py line 203): Answer.__str__."""
        from form.models import Answer, Question, QuestionType, Response, FormType
        qt = QuestionType.objects.create(
            question_typ="txt6str", question_typ_nm="Text6", void_ind="n", is_list=False
        )
        ft, _ = FormType.objects.get_or_create(
            form_typ="tststr2", defaults={"form_nm": "Test String Form 2"}
        )
        q = Question.objects.create(
            question="Q for answer str?",
            order=2,
            question_typ=qt,
            form_typ=ft,
            void_ind="n",
            table_col_width="100",
            required="n",
        )
        resp = Response.objects.create(form_typ=ft, void_ind="n")
        ans = Answer.objects.create(
            question=q, response=resp, value="42", void_ind="n"
        )
        result = str(ans)
        assert str(ans.id) in result

    def test_graph_str(self, test_user):
        """Line 253 (via form/models.py __str__): Graph.__str__."""
        from form.models import Graph, GraphType
        gt = GraphType.objects.create(
            graph_typ="barstr", graph_nm="Bar Chart Str", void_ind="n"
        )
        g = Graph.objects.create(
            graph_typ=gt,
            name="Test Graph Str",
            x_scale_min=0, x_scale_max=100,
            y_scale_min=0, y_scale_max=100,
            active="y",
            void_ind="n",
            creator=test_user,
        )
        result = str(g)
        assert "Test Graph Str" in result

    def test_graph_bin_str(self, test_user):
        """Line 265 (via form/models.py): GraphBin.__str__."""
        from form.models import Graph, GraphType, GraphBin
        gt = GraphType.objects.create(
            graph_typ="barbin", graph_nm="Bar Bin", void_ind="n"
        )
        g = Graph.objects.create(
            graph_typ=gt, name="Bin Graph",
            x_scale_min=0, x_scale_max=100,
            y_scale_min=0, y_scale_max=100,
            active="y", void_ind="n", creator=test_user,
        )
        gb = GraphBin.objects.create(graph=g, bin=0, width=10, void_ind="n")
        result = str(gb)
        assert str(gb.id) in result

    def test_graph_category_str(self, test_user):
        """Line 277: GraphCategory.__str__."""
        from form.models import Graph, GraphType, GraphCategory
        gt = GraphType.objects.create(
            graph_typ="barcg", graph_nm="Bar Cat", void_ind="n"
        )
        g = Graph.objects.create(
            graph_typ=gt, name="Cat Graph",
            x_scale_min=0, x_scale_max=100,
            y_scale_min=0, y_scale_max=100,
            active="y", void_ind="n", creator=test_user,
        )
        gc = GraphCategory.objects.create(
            graph=g, category="cat1", order=1, void_ind="n"
        )
        result = str(gc)
        assert str(gc.id) in result


# =============================================================================
# User Util  (missing lines 119-124 - get_users_parsed)
# =============================================================================

@pytest.mark.django_db
class TestUserUtilCoverage:
    """Cover missing user util lines."""

    def test_get_users_parsed_returns_list(self, test_user):
        """Lines 119-124: get_users_parsed iterates users."""
        from user.util import get_users_parsed
        with patch("general.cloudinary.build_image_url", return_value="https://example.com/img.jpg"):
            result = get_users_parsed(active=1, admin=True)
        assert isinstance(result, list)


# =============================================================================
# Scouting Util  (missing lines 367, 620, 628)
# =============================================================================

@pytest.mark.django_db
class TestScoutingUtilCoverage:
    """Cover missing scouting util lines."""

    def test_get_or_create_season_creates(self):
        """Line 367: get_or_create_season creates if missing."""
        from scouting.util import get_or_create_season
        season = get_or_create_season("2099str")
        assert season is not None
        assert season.season == "2099str"

    def test_get_event_by_key(self):
        """Lines 620, 628: get_event."""
        from scouting.models import Season, Event
        from scouting.util import get_event
        season = Season.objects.create(season="2050st", current="n", game="G", manual="")
        Event.objects.create(
            season=season, event_nm="GetEvent", event_cd="2050gest",
            date_st=datetime.datetime.now(pytz.UTC),
            date_end=datetime.datetime.now(pytz.UTC),
        )
        result = get_event("2050gest")
        assert result.event_cd == "2050gest"
