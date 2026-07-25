"""
Easy-win coverage tests for the scouting app.
Covers:
  - scouting/admin.py line 1 (already covered by import test in test_admin_coverage.py,
    but listed for completeness — no new test needed)
  - scouting/field/serializers.py line 20  (FieldResponseAnswerSerializer.to_representation)
  - scouting/models.py lines 231, 279, 291, 303 (__str__ methods)
  - scouting/serializers.py line 108  (get_sch_nm dict case)
  - scouting/util.py lines 620, 628  (get_scout_field_schedule / get_field_form)
  - scouting/views.py lines 216-217  (ScoutFieldScheduleSerializer call on success)
  - scouting/pit/views.py line 63  (type(ret) == Response branch)
"""
import pytest
from unittest.mock import patch, MagicMock
from rest_framework.response import Response as DRFResponse
import datetime


# ---------------------------------------------------------------------------
# scouting/field/serializers.py line 20
# ---------------------------------------------------------------------------
class TestFieldResponseAnswerSerializer:
    """FieldResponseAnswerSerializer.to_representation returns its input."""

    def test_to_representation_returns_instance(self):
        from scouting.field.serializers import FieldResponseAnswerSerializer
        s = FieldResponseAnswerSerializer()
        data = {"key": "value", "number": 42}
        assert s.to_representation(data) == data


# ---------------------------------------------------------------------------
# scouting/models.py lines 231, 279, 291, 303  (__str__ methods)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestScoutingModelStrMethods:
    """Test __str__ methods not yet covered."""

    def _make_season(self):
        from scouting.models import Season
        return Season.objects.create(season="2099s", current="y", game="G", manual="M")

    def _make_event(self, season):
        from scouting.models import Event
        return Event.objects.create(
            season=season,
            event_nm="Test Event",
            event_cd="2099s_test",
            date_st=datetime.date(2099, 3, 1),
            date_end=datetime.date(2099, 3, 3),
            current="y",
            void_ind="n",
        )

    def test_field_schedule_str(self):
        """Line 231: FieldSchedule.__str__"""
        from scouting.models import FieldSchedule
        season = self._make_season()
        event = self._make_event(season)
        fs = FieldSchedule.objects.create(
            event=event,
            st_time=datetime.datetime(2099, 3, 1, 9, 0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2099, 3, 1, 10, 0, tzinfo=datetime.timezone.utc),
            void_ind="n",
        )
        s = str(fs)
        assert str(fs.id) in s

    def test_question_str(self):
        """Line 279: scouting.Question.__str__"""
        from scouting.models import Question as ScoutQuestion, Season
        import form.models as fm
        season = self._make_season()
        qt = fm.QuestionType.objects.create(question_typ="num_sq", question_typ_nm="Number SQ")
        ftype = fm.FormType.objects.create(form_typ="field_sq", form_typ_nm="Field SQ")
        q = fm.Question.objects.create(
            question="Test SQ Question",
            question_typ=qt,
            form_typ=ftype,
            active="y",
            void_ind="n",
        )
        sq = ScoutQuestion.objects.create(question=q, season=season, void_ind="n")
        s = str(sq)
        assert str(sq.id) in s

    def test_question_flow_str(self):
        """Line 291: scouting.QuestionFlow.__str__"""
        from scouting.models import QuestionFlow, Season
        import form.models as fm
        season = self._make_season()
        flow = fm.Flow.objects.create(name="Test Flow SQ", void_ind="n")
        qf = QuestionFlow.objects.create(flow=flow, season=season, void_ind="n")
        s = str(qf)
        assert str(qf.id) in s

    def test_graph_str(self):
        """Line 303: scouting.Graph.__str__"""
        from scouting.models import Graph as ScoutGraph, Season
        import form.models as fm
        season = self._make_season()
        graph_typ = fm.GraphType.objects.create(
            graph_typ="histogram_sg", graph_typ_nm="Histogram SG"
        )
        g = fm.Graph.objects.create(
            name="Test Graph SQ",
            graph_typ=graph_typ,
            void_ind="n",
        )
        sg = ScoutGraph.objects.create(graph=g, season=season, void_ind="n")
        s = str(sg)
        assert str(sg.id) in s


# ---------------------------------------------------------------------------
# scouting/serializers.py line 108  (get_sch_nm dict case)
# ---------------------------------------------------------------------------
class TestScoutFieldScheduleSerializerGetSchNm:
    """Line 108: get_sch_nm handles dict obj."""

    def test_get_sch_nm_with_dict(self):
        from scouting.serializers import ScoutFieldScheduleSerializer
        s = ScoutFieldScheduleSerializer()
        # obj is a dict (not a model instance)
        obj = {"sch_nm": "Pit Schedule"}
        result = s.get_sch_nm(obj)
        assert result == "Pit Schedule"

    def test_get_sch_nm_with_dict_missing_key(self):
        from scouting.serializers import ScoutFieldScheduleSerializer
        s = ScoutFieldScheduleSerializer()
        obj = {}
        result = s.get_sch_nm(obj)
        assert result == ""


# ---------------------------------------------------------------------------
# scouting/util.py lines 620, 628
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestScoutingUtilExtra:
    """Lines 620, 628: get_scout_field_schedule and get_field_form."""

    def test_get_scout_field_schedule(self):
        """Line 620: get_scout_field_schedule returns FieldSchedule by id."""
        from scouting.models import Season, Event, FieldSchedule
        from scouting.util import get_scout_field_schedule
        import datetime

        season = Season.objects.create(season="2099u", current="y", game="G", manual="M")
        event = Event.objects.create(
            season=season, event_nm="U Event", event_cd="2099u_ev",
            date_st=datetime.date(2099, 4, 1), date_end=datetime.date(2099, 4, 3),
            current="y", void_ind="n",
        )
        fs = FieldSchedule.objects.create(
            event=event,
            st_time=datetime.datetime(2099, 4, 1, 9, 0, tzinfo=datetime.timezone.utc),
            end_time=datetime.datetime(2099, 4, 1, 10, 0, tzinfo=datetime.timezone.utc),
            void_ind="n",
        )
        result = get_scout_field_schedule(fs.id)
        assert result.id == fs.id

    def test_get_field_form_returns_dict(self):
        """Line 628: get_field_form returns parsed dict with 'id' key."""
        from scouting.util import get_field_form
        from scouting.models import Season, FieldForm

        season = Season.objects.create(season="2099ff", current="y", game="G", manual="M")

        ff = FieldForm.objects.create(season=season)

        with patch("scouting.util.get_current_season", return_value=season):
            result = get_field_form()

        assert result["id"] == ff.id
        assert "season_id" in result


# ---------------------------------------------------------------------------
# scouting/views.py lines 216-217  (success serializer call)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestScoutFieldScheduleView:
    """Lines 216-217: ScoutFieldScheduleSerializer called on success."""

    url = "/scouting/scout-field-schedule/"

    def test_get_returns_serialized_data(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        mock_data = [{"id": 1, "event_id": 1, "st_time": "2099-03-01T09:00:00Z",
                      "end_time": "2099-03-01T10:00:00Z"}]
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.views.scouting.util.get_current_scout_field_schedule_parsed",
                   return_value=mock_data), \
             patch("scouting.views.ScoutFieldScheduleSerializer") as MockSer:
            MockSer.return_value.data = mock_data
            response = api_client.get(self.url)
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# scouting/pit/views.py line 63  (type(ret) == Response branch)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPitResponsesViewReturnResponse:
    """Line 63: when get_responses returns a Response, it's returned directly."""

    url = "/scouting/pit/responses/"

    def test_get_when_util_returns_response(self, api_client, test_user):
        """Line 62-63: get_responses returns a Response object → returned directly."""
        api_client.force_authenticate(user=test_user)
        direct_response = DRFResponse({"detail": "direct"})
        with patch("scouting.views.has_access", return_value=True), \
             patch("scouting.pit.views.scouting.pit.util.get_responses",
                   return_value=direct_response), \
             patch("scouting.pit.views.access_response",
                   side_effect=lambda url, uid, auth, msg, fun: fun()):
            response = api_client.get(self.url)
        assert response.status_code == 200
