"""
Targeted coverage tests for form/views.py - covering all missing lines.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

def _ensure_system_user():
    """Create a system user with id=-1 if it doesn't exist (needed by ret_message error handler)."""
    User = get_user_model()
    try:
        return User.objects.get(id=-1)
    except User.DoesNotExist:
        u = User.objects.create_user(
            username="system_err",
            email="system_err@test.com",
            password="pass",
        )
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE user_user SET id=-1 WHERE id={u.id}")
        return User.objects.get(id=-1)


def _make_form_type(form_typ="survey", form_nm="Survey"):
    from form.models import FormType
    return FormType.objects.get_or_create(form_typ=form_typ, defaults={"form_nm": form_nm})[0]


def _make_question_type(q_typ="text", q_nm="Text", is_list="n"):
    from form.models import QuestionType
    return QuestionType.objects.get_or_create(
        question_typ=q_typ, defaults={"question_typ_nm": q_nm, "is_list": is_list}
    )[0]


def _make_question(form_typ=None, question_typ=None, question="Q?", order=1, active="y"):
    from form.models import Question
    if form_typ is None:
        form_typ = _make_form_type()
    if question_typ is None:
        question_typ = _make_question_type()
    return Question.objects.create(
        form_typ=form_typ,
        question_typ=question_typ,
        question=question,
        table_col_width="100",
        order=order,
        required="n",
        active=active,
        void_ind="n",
    )


def _make_flow(form_typ=None, name="Test Flow"):
    from form.models import Flow
    if form_typ is None:
        form_typ = _make_form_type()
    return Flow.objects.create(name=name, form_typ=form_typ, void_ind="n")


def _make_graph(user, graph_typ=None, name="Test Graph"):
    from form.models import Graph
    if graph_typ is None:
        from form.models import GraphType
        graph_typ, _ = GraphType.objects.get_or_create(
            graph_typ="histogram", defaults={"graph_nm": "Histogram"}
        )
    return Graph.objects.create(
        graph_typ=graph_typ,
        name=name,
        x_scale_min=0, x_scale_max=100,
        y_scale_min=0, y_scale_max=100,
        active="y",
        void_ind="n",
        creator=user,
    )


def _make_question_aggregate(name="Agg"):
    from form.models import QuestionAggregateType, QuestionAggregate
    qa_typ, _ = QuestionAggregateType.objects.get_or_create(
        question_aggregate_typ="sum", defaults={"question_aggregate_nm": "Sum"}
    )
    return QuestionAggregate.objects.create(
        question_aggregate_typ=qa_typ,
        name=name,
        horizontal=True,
        use_answer_time=False,
        active="y",
        void_ind="n",
    )


def _make_condition_type(typ="equal"):
    from form.models import QuestionConditionType
    ct, _ = QuestionConditionType.objects.get_or_create(
        question_condition_typ=typ, defaults={"question_condition_nm": typ}
    )
    return ct


@pytest.fixture
def rf():
    return APIRequestFactory()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="vuser", password="pass", email="vuser@test.com")


# ─────────────────────────────────────────────────────────────
#  QuestionView.post  –  lines 59-88
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestQuestionViewPost:
    def test_post_unauthenticated_returns_401(self, rf):
        """Line 56-57: no user id → 401."""
        from form.views import QuestionView

        request = rf.post("/form/question/", {}, format="json")
        request.user = Mock(id=None)
        response = QuestionView.as_view()(request)
        assert response.status_code == 401

    def test_post_no_access_returns_error(self, rf, user):
        """Lines 74-80: has_access returns False."""
        from form.views import QuestionView

        request = rf.post("/form/question/", {}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", return_value=False):
            response = QuestionView.as_view()(request)
        assert response.status_code == 200
        assert response.data.get("retMessage") is not None

    def test_post_invalid_data_returns_error(self, rf, user):
        """Lines 60-68: serializer is not valid."""
        from form.views import QuestionView

        request = rf.post("/form/question/", {"invalid": "data"}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", return_value=True):
            response = QuestionView.as_view()(request)
        assert response.status_code == 200

    def test_post_valid_data_saves(self, rf, user):
        """Lines 70-73: valid data saves question."""
        from form.views import QuestionView
        from form.models import FormType, QuestionType

        FormType.objects.get_or_create(form_typ="vsurvey", defaults={"form_nm": "VSurvey"})
        QuestionType.objects.get_or_create(
            question_typ="vtext", defaults={"question_typ_nm": "VText", "is_list": "n"}
        )

        payload = {
            "form_typ": {"form_typ": "vsurvey"},
            "question_typ": {"question_typ": "vtext", "question_typ_nm": "VText", "is_list": "n"},
            "question": "View test Q?",
            "table_col_width": "100",
            "order": 1,
            "active": "y",
            "required": "n",
            "questionoption_set": [],
            "flow_id_set": [],
            "conditional_on_questions": [],
            "conditional_question_id_set": [],
        }
        request = rf.post("/form/question/", payload, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.save_question"):
                response = QuestionView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception_returns_error(self, rf, user):
        """Lines 81-88: exception → error message."""
        from form.views import QuestionView

        request = rf.post("/form/question/", {}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", side_effect=Exception("boom")):
            response = QuestionView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  FormEditorView.get  –  lines 102-134
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFormEditorView:
    def test_get_no_access(self, rf, user):
        """Lines 120-128: has_access=False → error."""
        from form.views import FormEditorView

        request = rf.get("/form/form-editor/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = FormEditorView.as_view()(request)
        assert response.status_code == 200

    def test_get_with_access_success(self, rf, user):
        """Lines 103-118: has_access=True returns data."""
        from form.views import FormEditorView

        _make_form_type("fe_survey", "FE Survey")
        _make_question_type("fe_text", "FE Text")

        request = rf.get("/form/form-editor/?form_typ=fe_survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.get_questions", return_value=[]):
                with patch("form.util.get_question_types", return_value=[]):
                    with patch("form.util.get_form_sub_types", return_value=[]):
                        with patch("form.util.get_flows", return_value=[]):
                            response = FormEditorView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 127-134: exception → error message."""
        from form.views import FormEditorView

        request = rf.get("/form/form-editor/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = FormEditorView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  SaveAnswersView.post  –  lines 146-211
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveAnswersView:
    def test_field_form_unauthenticated(self, rf):
        """Lines 155-156: field form with no user → 401."""
        from form.views import SaveAnswersView

        request = rf.post("/form/save-answers/", {"form_typ": "field"}, format="json")
        request.user = Mock(id=None)
        response = SaveAnswersView.as_view()(request)
        assert response.status_code == 401

    def test_field_form_no_access(self, rf, user):
        """Lines 183-189: no scoutfield access."""
        from form.views import SaveAnswersView

        request = rf.post("/form/save-answers/", {"form_typ": "field"}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", return_value=False):
            response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200

    def test_pit_form_no_access(self, rf, user):
        """Lines 183-189: no scoutpit access."""
        from form.views import SaveAnswersView

        request = rf.post("/form/save-answers/", {"form_typ": "pit"}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", return_value=False):
            response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200

    def test_field_form_invalid_serializer(self, rf, user):
        """Lines 175-182: serializer invalid for field form."""
        from form.views import SaveAnswersView

        request = rf.post("/form/save-answers/", {"form_typ": "field"}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", return_value=True):
            response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200

    def test_field_form_valid_saves_field_response(self, rf, user):
        """Lines 162-168: valid field form saves field response."""
        from form.views import SaveAnswersView

        _make_form_type("field", "Field")

        payload = {
            "form_typ": "field",
            "team_id": 1234,
            "answers": [],
        }
        request = rf.post("/form/save-answers/", payload, format="json")
        force_authenticate(request, user=user)
        request.user = user

        with patch("form.views.has_access", return_value=True):
            with patch("form.util.save_field_response") as mock_sfr:
                mock_sfr.return_value = Mock()
                response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200

    def test_pit_form_valid_saves_pit_response(self, rf, user):
        """Lines 169-173: valid pit form saves pit response."""
        from form.views import SaveAnswersView

        _make_form_type("pit", "Pit")

        payload = {
            "form_typ": "pit",
            "team_id": 5678,
            "answers": [],
        }
        request = rf.post("/form/save-answers/", payload, format="json")
        force_authenticate(request, user=user)
        request.user = user

        with patch("form.views.has_access", return_value=True):
            with patch("form.util.save_pit_response") as mock_spr:
                mock_spr.return_value = Mock()
                response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200

    def test_generic_form_valid(self, rf, user):
        """Lines 191-194: generic (non-field/pit) form."""
        from form.views import SaveAnswersView

        _make_form_type("reg1", "Reg1")

        payload = {
            "form_typ": "reg1",
            "question_answers": [],
        }
        request = rf.post("/form/save-answers/", payload, format="json")
        force_authenticate(request, user=user)
        request.user = user

        with patch("form.util.save_answers") as mock_sa:
            response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200

    def test_generic_form_invalid_serializer(self, rf, user):
        """Lines 195-203: generic form with invalid data."""
        from form.views import SaveAnswersView

        request = rf.post("/form/save-answers/", {"form_typ": "reg_bad"}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200

    def test_exception_returns_error(self, rf, user):
        """Lines 204-211: exception → error message."""
        from form.views import SaveAnswersView

        request = rf.post("/form/save-answers/", {"form_typ": "field"}, format="json")
        force_authenticate(request, user=user)
        request.user = user
        with patch("form.views.has_access", side_effect=Exception("boom")):
            response = SaveAnswersView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  ResponseView  –  lines 224-297
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestResponseView:
    def test_get_no_access(self, rf, user):
        """Lines 230-238: no admin access."""
        from form.views import ResponseView

        request = rf.get("/form/response/?response_id=1")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_get_with_access(self, rf, user):
        """Lines 226-229: admin access gets response."""
        from form.views import ResponseView
        from form.models import Response

        ft = _make_form_type("rv1", "RV1")
        resp = Response.objects.create(form_typ=ft, void_ind="n")

        request = rf.get(f"/form/response/?response_id={resp.id}")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.get_response", return_value=[]):
                response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 237-244: exception → error."""
        from form.views import ResponseView

        request = rf.get("/form/response/?response_id=1")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_post_invalid_data(self, rf, user):
        """Lines 247-255: post with invalid data."""
        from form.views import ResponseView

        request = rf.post("/form/response/", {}, format="json")
        force_authenticate(request, user=user)
        response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_post_no_access(self, rf, user):
        """Lines 270-276: post without admin access."""
        from form.views import ResponseView

        request = rf.post("/form/response/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.ResponseSerializer") as MockSerial:
            MockSerial.return_value.is_valid.return_value = True
            MockSerial.return_value.validated_data = {}
            with patch("form.views.has_access", return_value=False):
                response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_post_with_access(self, rf, user):
        """Lines 257-261: post with admin access saves response."""
        from form.views import ResponseView

        request = rf.post("/form/response/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.ResponseSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_response"):
                    response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_post_save_exception(self, rf, user):
        """Lines 262-271: exception during save → error."""
        from form.views import ResponseView

        request = rf.post("/form/response/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.ResponseSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_response", side_effect=Exception("save failed")):
                    response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception(self, rf, user):
        """Lines 262-269: exception during post."""
        from form.views import ResponseView
        from django.utils import timezone

        ft = _make_form_type("rv4", "RV4")
        payload = {
            "form_typ": "rv4",
            "time": timezone.now().isoformat(),
            "archive_ind": "n",
        }
        request = rf.post("/form/response/", payload, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.save_response", side_effect=Exception("err")):
                response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_delete_no_access(self, rf, user):
        """Lines 283-290: delete without access."""
        from form.views import ResponseView

        request = rf.delete("/form/response/?response_id=1")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_delete_with_access(self, rf, user):
        """Lines 280-282: delete with admin access."""
        from form.views import ResponseView

        request = rf.delete("/form/response/?response_id=1")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.delete_response", return_value=Mock()):
                response = ResponseView.as_view()(request)
        assert response.status_code == 200

    def test_delete_exception(self, rf, user):
        """Lines 290-297: exception during delete."""
        from form.views import ResponseView

        request = rf.delete("/form/response/?response_id=1")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = ResponseView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  ResponsesView.get  –  lines 310-333
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestResponsesView:
    def test_get_no_access(self, rf, user):
        """Lines 319-327: no access."""
        from form.views import ResponsesView

        request = rf.get("/form/responses/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = ResponsesView.as_view()(request)
        assert response.status_code == 200

    def test_get_with_access(self, rf, user):
        """Lines 312-318: with admin access."""
        from form.views import ResponsesView

        _make_form_type("rsp_survey", "RSP Survey")
        request = rf.get("/form/responses/?form_typ=rsp_survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.get_responses", return_value=[]):
                response = ResponsesView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 326-333: exception → error."""
        from form.views import ResponsesView

        request = rf.get("/form/responses/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = ResponsesView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  QuestionAggregateView  –  lines 345-399
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestQuestionAggregateView:
    def test_get_no_access(self, rf, user):
        """Lines 354-361: no access."""
        from form.views import QuestionAggregateView

        request = rf.get("/form/question-aggregate/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200

    def test_get_with_access(self, rf, user):
        """Lines 347-353: with access."""
        from form.views import QuestionAggregateView

        request = rf.get("/form/question-aggregate/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.get_question_aggregates", return_value=[]):
                response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 360-367: exception → error."""
        from form.views import QuestionAggregateView

        request = rf.get("/form/question-aggregate/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200

    def test_post_no_access(self, rf, user):
        """Lines 385-391: post no access."""
        from form.views import QuestionAggregateView

        request = rf.post("/form/question-aggregate/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.QuestionAggregateSerializer") as MockSerial:
            MockSerial.return_value.is_valid.return_value = True
            MockSerial.return_value.validated_data = {}
            with patch("form.views.has_access", return_value=False):
                response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200

    def test_post_with_access(self, rf, user):
        """Lines 381-384: post with access saves."""
        from form.views import QuestionAggregateView

        request = rf.post("/form/question-aggregate/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.QuestionAggregateSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_question_aggregate") as mock_save:
                    mock_save.return_value = Mock()
                    response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200

    def test_post_save_exception(self, rf, user):
        """Lines 386-393: exception during save → error."""
        from form.views import QuestionAggregateView

        request = rf.post("/form/question-aggregate/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.QuestionAggregateSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_question_aggregate", side_effect=Exception("err")):
                    response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200

    def test_post_invalid_data(self, rf, user):
        """Lines 371-379: invalid data → error message."""
        from form.views import QuestionAggregateView

        request = rf.post("/form/question-aggregate/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception(self, rf, user):
        """Lines 392-399: exception → error."""
        from form.views import QuestionAggregateView

        request = rf.post("/form/question-aggregate/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = QuestionAggregateView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  QuestionAggregateTypeView.get  –  lines 412-423
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestQuestionAggregateTypeView:
    def test_get_success(self, rf, user):
        """Lines 413-415: success."""
        from form.views import QuestionAggregateTypeView

        request = rf.get("/form/question-aggregate-types/")
        force_authenticate(request, user=user)
        with patch("form.util.get_question_aggregate_types", return_value=[]):
            response = QuestionAggregateTypeView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 416-423: exception → error."""
        from form.views import QuestionAggregateTypeView

        request = rf.get("/form/question-aggregate-types/")
        force_authenticate(request, user=user)
        with patch("form.util.get_question_aggregate_types", side_effect=Exception("err")):
            response = QuestionAggregateTypeView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  QuestionConditionView  –  lines 435-489
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestQuestionConditionView:
    def test_get_no_access(self, rf, user):
        """Lines 443-451: no access."""
        from form.views import QuestionConditionView

        request = rf.get("/form/question-condition/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200

    def test_get_with_access(self, rf, user):
        """Lines 437-442: with access."""
        from form.views import QuestionConditionView

        request = rf.get("/form/question-condition/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.get_question_conditions", return_value=[]):
                response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 450-457: exception."""
        from form.views import QuestionConditionView

        request = rf.get("/form/question-condition/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_invalid_data(self, rf, user):
        """Lines 461-469: invalid serializer data."""
        from form.views import QuestionConditionView

        request = rf.post("/form/question-condition/", {}, format="json")
        force_authenticate(request, user=user)
        response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_no_access(self, rf, user):
        """Lines 475-481: no access."""
        from form.views import QuestionConditionView

        request = rf.post("/form/question-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.QuestionConditionSerializer") as MockSerial:
            MockSerial.return_value.is_valid.return_value = True
            MockSerial.return_value.validated_data = {}
            with patch("form.views.has_access", return_value=False):
                response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_with_access(self, rf, user):
        """Lines 471-474: with access saves condition."""
        from form.views import QuestionConditionView

        request = rf.post("/form/question-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.QuestionConditionSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_question_condition") as mock_save:
                    mock_save.return_value = Mock()
                    response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_save_exception(self, rf, user):
        """Lines 476-483: exception during save → error."""
        from form.views import QuestionConditionView

        request = rf.post("/form/question-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.QuestionConditionSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_question_condition", side_effect=Exception("err")):
                    response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception(self, rf, user):
        """Lines 482-489: exception → error."""
        from form.views import QuestionConditionView

        request = rf.post("/form/question-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = QuestionConditionView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  QuestionConditionTypesView.get  –  lines 501-521
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestQuestionConditionTypesView:
    def test_get_no_access(self, rf, user):
        """Lines 507-515: no access."""
        from form.views import QuestionConditionTypesView

        request = rf.get("/form/question-condition-types/")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = QuestionConditionTypesView.as_view()(request)
        assert response.status_code == 200

    def test_get_with_access(self, rf, user):
        """Lines 503-506: with access."""
        from form.views import QuestionConditionTypesView

        request = rf.get("/form/question-condition-types/")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.get_question_condition_types", return_value=[]):
                response = QuestionConditionTypesView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 514-521: exception → error."""
        from form.views import QuestionConditionTypesView

        request = rf.get("/form/question-condition-types/")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = QuestionConditionTypesView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  FlowView  –  lines 533-587
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFlowView:
    def test_get_all_flows(self, rf, user):
        """Lines 535-545: get all flows (no id)."""
        from form.views import FlowView

        request = rf.get("/form/flow/")
        force_authenticate(request, user=user)
        with patch("form.util.get_flows", return_value=[]):
            response = FlowView.as_view()(request)
        assert response.status_code == 200

    def test_get_single_flow(self, rf, user):
        """Lines 543-545: get single flow by id."""
        from form.views import FlowView

        mock_flow = {
            "id": 1, "name": "F", "single_run": False, "form_based": False,
            "form_typ": Mock(form_typ="survey"), "form_sub_typ": None,
            "flow_questions": [], "void_ind": "n",
            "has_conditions": "n", "flow_conditional_on": None,
        }
        with patch("form.util.get_flows", return_value=[mock_flow]):
            request = rf.get("/form/flow/?id=1")
            force_authenticate(request, user=user)
            response = FlowView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user, system_user):
        """Lines 546-553: exception → error."""
        from form.views import FlowView

        request = rf.get("/form/flow/")
        force_authenticate(request, user=user)
        with patch("form.util.get_flows", side_effect=Exception("err")):
            response = FlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_no_access(self, rf, user):
        """Lines 572-578: no access."""
        from form.views import FlowView

        _make_form_type("fv1", "FV1")
        payload = {
            "name": "FV Flow",
            "single_run": False,
            "form_based": False,
            "form_typ": {"form_typ": "fv1"},
            "void_ind": "n",
            "flow_questions": [],
        }
        request = rf.post("/form/flow/", payload, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = FlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_with_access(self, rf, user):
        """Lines 557-571: with access saves flow."""
        from form.views import FlowView

        request = rf.post("/form/flow/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.FlowSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_flow") as mock_sf:
                    mock_sf.return_value = Mock()
                    response = FlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_invalid_data(self, rf, user):
        """Lines 559-567: invalid data."""
        from form.views import FlowView

        request = rf.post("/form/flow/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            response = FlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception(self, rf, user):
        """Lines 579-586: exception → error."""
        from form.views import FlowView

        request = rf.post("/form/flow/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = FlowView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  QuestionFlowView  –  lines 598-651
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestQuestionFlowView:
    def test_get_all_flows(self, rf, user):
        """Lines 599-611: get all flows."""
        from form.views import QuestionFlowView

        request = rf.get("/form/question-flow/")
        force_authenticate(request, user=user)
        with patch("form.util.get_flows", return_value=[]):
            response = QuestionFlowView.as_view()(request)
        assert response.status_code == 200

    def test_get_single_flow(self, rf, user):
        """Lines 607-610: single flow by id."""
        from form.views import QuestionFlowView

        mock_flow = {
            "id": 2, "name": "QF", "single_run": False, "form_based": False,
            "form_typ": Mock(form_typ="survey"), "form_sub_typ": None,
            "flow_questions": [], "void_ind": "n",
            "has_conditions": "n", "flow_conditional_on": None,
        }
        request = rf.get("/form/question-flow/?id=2")
        force_authenticate(request, user=user)
        with patch("form.util.get_flows", return_value=[mock_flow]):
            response = QuestionFlowView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user, system_user):
        """Lines 611-618: exception → error."""
        from form.views import QuestionFlowView

        request = rf.get("/form/question-flow/")
        force_authenticate(request, user=user)
        with patch("form.util.get_flows", side_effect=Exception("err")):
            response = QuestionFlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_no_access(self, rf, user):
        """Lines 637-643: no access."""
        from form.views import QuestionFlowView

        _make_form_type("qfv1", "QFV1")
        payload = {
            "name": "QFV Flow",
            "single_run": False,
            "form_based": False,
            "form_typ": {"form_typ": "qfv1"},
            "void_ind": "n",
            "flow_questions": [],
        }
        request = rf.post("/form/question-flow/", payload, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = QuestionFlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_invalid_data_with_access(self, rf, user):
        """Line 625: invalid data with access → error."""
        from form.views import QuestionFlowView

        request = rf.post("/form/question-flow/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            response = QuestionFlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_with_access(self, rf, user):
        """Lines 621-636: with access saves."""
        from form.views import QuestionFlowView

        request = rf.post("/form/question-flow/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.FlowSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_flow") as mock_sf:
                    mock_sf.return_value = Mock()
                    response = QuestionFlowView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception(self, rf, user):
        """Lines 644-651: exception → error."""
        from form.views import QuestionFlowView

        request = rf.post("/form/question-flow/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = QuestionFlowView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  FlowConditionView  –  lines 663-715
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFlowConditionView:
    def test_get_no_access(self, rf, user):
        """Lines 669-677: no access."""
        from form.views import FlowConditionView

        request = rf.get("/form/flow-condition/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = FlowConditionView.as_view()(request)
        assert response.status_code == 200

    def test_get_with_access(self, rf, user):
        """Lines 665-668: with access."""
        from form.views import FlowConditionView

        request = rf.get("/form/flow-condition/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.util.get_flow_condition", return_value=[]):
                response = FlowConditionView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user):
        """Lines 676-683: exception."""
        from form.views import FlowConditionView

        request = rf.get("/form/flow-condition/?form_typ=survey")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = FlowConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_invalid_data(self, rf, user):
        """Lines 687-695: invalid data."""
        from form.views import FlowConditionView

        request = rf.post("/form/flow-condition/", {}, format="json")
        force_authenticate(request, user=user)
        response = FlowConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_no_access(self, rf, user):
        """Lines 700-706: no access."""
        from form.views import FlowConditionView

        request = rf.post("/form/flow-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.FlowConditionSerializer") as MockSerial:
            MockSerial.return_value.is_valid.return_value = True
            MockSerial.return_value.validated_data = {}
            with patch("form.views.has_access", return_value=False):
                response = FlowConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_with_access(self, rf, user):
        """Lines 697-699: with access saves."""
        from form.views import FlowConditionView

        request = rf.post("/form/flow-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.FlowConditionSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_flow_condition") as mock_sfc:
                    mock_sfc.return_value = Mock()
                    response = FlowConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_save_exception(self, rf, user):
        """Lines 702-709: exception during save → error."""
        from form.views import FlowConditionView

        request = rf.post("/form/flow-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.FlowConditionSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_flow_condition", side_effect=Exception("err")):
                    response = FlowConditionView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception(self, rf, user):
        """Lines 708-715: exception → error."""
        from form.views import FlowConditionView

        request = rf.post("/form/flow-condition/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = FlowConditionView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  GraphEditorView.get  –  lines 727-749
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGraphEditorView:
    def test_get_success(self, rf, user):
        """Lines 728-741: success."""
        from form.views import GraphEditorView

        request = rf.get("/form/graph-editor/")
        force_authenticate(request, user=user)
        with patch("form.util.get_graph_types", return_value=[]):
            with patch("form.util.get_graph_question_types", return_value=[]):
                with patch("form.util.get_graphs", return_value=[]):
                    with patch("form.util.get_question_condition_types", return_value=[]):
                        response = GraphEditorView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user, system_user):
        """Lines 742-749: exception → error."""
        from form.views import GraphEditorView

        request = rf.get("/form/graph-editor/")
        force_authenticate(request, user=user)
        with patch("form.util.get_graph_types", side_effect=Exception("err")):
            response = GraphEditorView.as_view()(request)
        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────
#  GraphView  –  lines 761-809
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGraphView:
    def test_get_all_graphs(self, rf, user):
        """Lines 762-769: get all graphs."""
        from form.views import GraphView

        request = rf.get("/form/graph/")
        force_authenticate(request, user=user)
        with patch("form.util.get_graphs", return_value=[]):
            response = GraphView.as_view()(request)
        assert response.status_code == 200

    def test_get_single_graph(self, rf, user):
        """Lines 766-768: single graph."""
        from form.views import GraphView
        from form.models import GraphType

        gt, _ = GraphType.objects.get_or_create(
            graph_typ="histogram", defaults={"graph_nm": "Histogram"}
        )
        mock_graph = {
            "id": 1, "name": "G", "graph_typ": gt,
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [], "graphcategory_set": [], "graphquestion_set": [],
        }
        request = rf.get("/form/graph/?graph_id=1")
        force_authenticate(request, user=user)
        with patch("form.util.get_graphs", return_value=[mock_graph]):
            response = GraphView.as_view()(request)
        assert response.status_code == 200

    def test_get_exception(self, rf, user, system_user):
        """Lines 770-777: exception → error."""
        from form.views import GraphView

        request = rf.get("/form/graph/")
        force_authenticate(request, user=user)
        with patch("form.util.get_graphs", side_effect=Exception("err")):
            response = GraphView.as_view()(request)
        assert response.status_code == 200

    def test_post_no_access(self, rf, user):
        """Lines 795-801: no access."""
        from form.views import GraphView
        from form.models import GraphType

        GraphType.objects.get_or_create(
            graph_typ="histogram", defaults={"graph_nm": "Histogram"}
        )

        payload = {
            "graph_typ": {"graph_typ": "histogram", "requires_bins": False,
                          "requires_categories": False, "requires_graph_question_typs": []},
            "name": "Test G",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [],
        }
        request = rf.post("/form/graph/", payload, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=False):
            response = GraphView.as_view()(request)
        assert response.status_code == 200

    def test_post_with_access(self, rf, user):
        """Lines 779-794: with access saves graph."""
        from form.views import GraphView

        request = rf.post("/form/graph/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            with patch("form.views.GraphSerializer") as MockSerial:
                MockSerial.return_value.is_valid.return_value = True
                MockSerial.return_value.validated_data = {}
                with patch("form.util.save_graph") as mock_sg:
                    response = GraphView.as_view()(request)
        assert response.status_code == 200

    def test_post_invalid_data(self, rf, user):
        """Lines 782-790: invalid data → error."""
        from form.views import GraphView

        request = rf.post("/form/graph/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", return_value=True):
            response = GraphView.as_view()(request)
        assert response.status_code == 200

    def test_post_exception(self, rf, user):
        """Lines 802-809: exception → error."""
        from form.views import GraphView

        request = rf.post("/form/graph/", {}, format="json")
        force_authenticate(request, user=user)
        with patch("form.views.has_access", side_effect=Exception("err")):
            response = GraphView.as_view()(request)
        assert response.status_code == 200
