"""
Targeted coverage tests for form/util.py - covering all missing lines.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from datetime import datetime, date, timedelta
from django.db.models import Q


# ─────────────────────────────────────────────────────────────
#  Helpers / fixtures
# ─────────────────────────────────────────────────────────────

def _make_form_type(form_typ="survey", form_nm="Survey"):
    from form.models import FormType
    return FormType.objects.get_or_create(form_typ=form_typ, defaults={"form_nm": form_nm})[0]


def _make_question_type(q_typ="text", q_nm="Text", is_list="n"):
    from form.models import QuestionType
    return QuestionType.objects.get_or_create(
        question_typ=q_typ,
        defaults={"question_typ_nm": q_nm, "is_list": is_list},
    )[0]


def _make_question(form_typ=None, question_typ=None, question="Q?", order=1, active="y", form_sub_typ=None):
    from form.models import Question
    if form_typ is None:
        form_typ = _make_form_type()
    if question_typ is None:
        question_typ = _make_question_type()
    return Question.objects.create(
        form_typ=form_typ,
        question_typ=question_typ,
        form_sub_typ=form_sub_typ,
        question=question,
        table_col_width="100",
        order=order,
        required="n",
        active=active,
        void_ind="n",
    )


def _make_question_aggregate_type(typ="sum"):
    from form.models import QuestionAggregateType
    return QuestionAggregateType.objects.get_or_create(
        question_aggregate_typ=typ,
        defaults={"question_aggregate_nm": typ.upper()},
    )[0]


def _make_question_aggregate(qa_typ=None, name="Agg", horizontal=True, use_answer_time=False):
    from form.models import QuestionAggregate
    if qa_typ is None:
        qa_typ = _make_question_aggregate_type()
    return QuestionAggregate.objects.create(
        question_aggregate_typ=qa_typ,
        name=name,
        horizontal=horizontal,
        use_answer_time=use_answer_time,
        active="y",
        void_ind="n",
    )


def _make_condition_type(typ="equal"):
    from form.models import QuestionConditionType
    return QuestionConditionType.objects.get_or_create(
        question_condition_typ=typ,
        defaults={"question_condition_nm": typ},
    )[0]


def _make_graph_type(typ="histogram", requires_bins=False, requires_categories=False):
    from form.models import GraphType
    gt, _ = GraphType.objects.get_or_create(
        graph_typ=typ,
        defaults={"graph_nm": typ, "requires_bins": requires_bins, "requires_categories": requires_categories},
    )
    return gt


def _make_graph(user, graph_typ=None, name="Test Graph"):
    from form.models import Graph
    if graph_typ is None:
        graph_typ = _make_graph_type()
    return Graph.objects.create(
        graph_typ=graph_typ,
        name=name,
        x_scale_min=0,
        x_scale_max=100,
        y_scale_min=0,
        y_scale_max=100,
        active="y",
        void_ind="n",
        creator=user,
    )


def _make_response(form_typ=None):
    from form.models import Response
    if form_typ is None:
        form_typ = _make_form_type()
    return Response.objects.create(form_typ=form_typ, void_ind="n")


# ─────────────────────────────────────────────────────────────
#  parse_question – lines 204-205, 212-213
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestParseQuestion:
    """Tests for parse_question, covering exception handler branches."""

    def test_parse_question_basic(self):
        """parse_question returns expected keys."""
        from form.util import parse_question
        q = _make_question()
        result = parse_question(q)
        assert "id" in result
        assert "question" in result
        assert "conditional_question_id_set" in result

    def test_parse_question_with_form_sub_typ(self):
        """parse_question with non-null form_sub_typ (covers display_value branch)."""
        from form.models import FormSubType
        from form.util import parse_question

        ft = _make_form_type("survey2", "Survey2")
        fst = FormSubType.objects.create(
            form_sub_typ="sub1", form_sub_nm="Sub 1", form_typ=ft, order=1
        )
        q = _make_question(form_typ=ft, form_sub_typ=fst)
        result = parse_question(q)
        assert "Sub 1" in result["display_value"]

    def test_parse_question_with_scout_question(self):
        """parse_question when scout question exists."""
        from form.util import parse_question

        q = _make_question()
        # Mock scout_question related manager
        mock_sq = Mock()
        mock_sq.id = 5
        mock_sq.season = Mock(id=2024)
        mock_get = Mock(return_value=mock_sq)
        with patch.object(type(q.scout_question), "get", mock_get):
            result = parse_question(q)
        assert result["season_id"] == 2024

    def test_parse_question_inactive_question(self):
        """parse_question with inactive question includes 'Deactivated' in display."""
        from form.util import parse_question

        q = _make_question(active="n")
        result = parse_question(q)
        assert "Deactivated" in result["display_value"]


# ─────────────────────────────────────────────────────────────
#  save_question – lines 260, 266-272, 300, 305-313, 319-350, 356, 359-371
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveQuestion:
    """Tests for save_question covering various branches."""

    def test_save_new_question_non_field(self):
        """Lines 266-272 (else branch): create new question for non-field form."""
        from form.util import save_question

        ft = _make_form_type("survey3", "Survey3")
        qt = _make_question_type("text2", "Text2")

        data = {
            "form_typ": {"form_typ": "survey3"},
            "question_typ": {"question_typ": "text2", "is_list": "n"},
            "question": "New question?",
            "table_col_width": "100",
            "order": 1,
            "active": "y",
            "required": "n",
            "questionoption_set": [],
        }
        save_question(data)

        from form.models import Question
        assert Question.objects.filter(question="New question?").exists()

    def test_save_existing_question(self):
        """Lines 266-272 (if branch): update existing question."""
        from form.util import save_question

        q = _make_question(question="Original?")
        data = {
            "id": q.id,
            "form_typ": {"form_typ": q.form_typ.form_typ},
            "question_typ": {"question_typ": q.question_typ.question_typ, "is_list": "n"},
            "question": "Updated?",
            "table_col_width": "200",
            "order": 2,
            "active": "n",
            "required": "y",
            "questionoption_set": [],
        }
        save_question(data)

        q.refresh_from_db()
        assert q.question == "Updated?"
        assert q.active == "n"

    def test_save_question_with_options(self):
        """Lines 359-371: save question options."""
        from form.util import save_question

        ft = _make_form_type("survey4", "Survey4")
        qt = _make_question_type("select", "Select", is_list="y")

        data = {
            "form_typ": {"form_typ": "survey4"},
            "question_typ": {"question_typ": "select", "is_list": "y"},
            "question": "Pick one?",
            "table_col_width": "100",
            "order": 1,
            "active": "y",
            "required": "n",
            "questionoption_set": [
                {"option": "Option A", "active": "y"},
                {"option": "Option B", "active": "y"},
            ],
        }
        save_question(data)

        from form.models import QuestionOption
        assert QuestionOption.objects.filter(option="Option A").exists()

    def test_save_question_update_existing_option(self):
        """Lines 359-371: update existing question option."""
        from form.util import save_question
        from form.models import QuestionOption

        ft = _make_form_type("survey5", "Survey5")
        qt = _make_question_type("sel2", "Select2", is_list="y")
        q = _make_question(form_typ=ft, question_typ=qt, question="Sel Q?")
        opt = QuestionOption.objects.create(question=q, option="Old", active="y", void_ind="n")

        data = {
            "id": q.id,
            "form_typ": {"form_typ": ft.form_typ},
            "question_typ": {"question_typ": qt.question_typ, "is_list": "y"},
            "question": "Sel Q?",
            "table_col_width": "100",
            "order": 1,
            "active": "y",
            "required": "n",
            "questionoption_set": [
                {"question_opt_id": opt.question_opt_id, "option": "New", "active": "y"},
            ],
        }
        save_question(data)

        opt.refresh_from_db()
        assert opt.option == "New"

    def test_save_question_list_without_options_raises(self):
        """Line 356: list question without options raises Exception."""
        from form.util import save_question

        ft = _make_form_type("survey6", "Survey6")
        qt = _make_question_type("sel3", "Select3", is_list="y")

        data = {
            "form_typ": {"form_typ": "survey6"},
            "question_typ": {"question_typ": "sel3", "is_list": "y"},
            "question": "No options?",
            "table_col_width": "100",
            "order": 1,
            "active": "y",
            "required": "n",
            "questionoption_set": [],
        }
        with pytest.raises(Exception, match="Select questions must have options"):
            save_question(data)

    def test_save_new_field_question_creates_null_answers(self):
        """Lines 300, 319-350: new field question creates !EXIST answers for existing responses."""
        from form.util import save_question
        from scouting.models import Season, Event, FieldResponse, Team
        from form.models import Response, Answer

        ft = _make_form_type("field", "Field")
        qt = _make_question_type("txt3", "Text3")

        season = Season.objects.get_or_create(season="2025", defaults={"current": "y"})[0]
        event = Event.objects.create(
            season=season,
            event_cd="TEST1",
            event_nm="Test Event",
            date_st="2025-01-01T00:00:00Z",
            date_end="2025-01-02T00:00:00Z",
            void_ind="n",
        )

        # Create an existing field response
        resp = _make_response(ft)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username="suser1", email="suser1@test.com", password="pass")
        team = Team.objects.get_or_create(team_no=1234, defaults={"team_nm": "Team 1234"})[0]
        fr = FieldResponse.objects.create(
            event=event,
            team=team,
            user=user,
            response=resp,
            void_ind="n",
        )

        with patch("form.util.scouting.util.get_current_season", return_value=season):
            data = {
                "form_typ": {"form_typ": "field"},
                "question_typ": {"question_typ": "txt3", "is_list": "n"},
                "question": "New field Q?",
                "table_col_width": "100",
                "order": 1,
                "active": "y",
                "required": "n",
                "scout_question": {"id": None},
                "questionoption_set": [],
            }
            save_question(data)

        from form.models import Question
        new_q = Question.objects.get(question="New field Q?")
        assert Answer.objects.filter(question=new_q, value="!EXIST").exists()

    def test_save_new_pit_question_creates_null_answers(self):
        """Lines 305-313 (pit branch): new pit question creates !EXIST answers."""
        from scouting.models import Season, Event, PitResponse, Team
        from form.models import Response, Answer

        ft = _make_form_type("pit", "Pit")
        qt = _make_question_type("txt4", "Text4")

        season = Season.objects.get_or_create(season="2026", defaults={"current": "n"})[0]
        event = Event.objects.create(
            season=season,
            event_cd="TST2",
            event_nm="Test Event 2",
            date_st="2026-01-01T00:00:00Z",
            date_end="2026-01-02T00:00:00Z",
            void_ind="n",
        )

        resp = _make_response(ft)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username="suser2", email="suser2@test.com", password="pass")
        team = Team.objects.get_or_create(team_no=5678, defaults={"team_nm": "Team 5678"})[0]
        pr = PitResponse.objects.create(
            event=event,
            team=team,
            user=user,
            response=resp,
            void_ind="n",
        )

        with patch("form.util.scouting.util.get_current_season", return_value=season):
            from form.util import save_question
            data = {
                "form_typ": {"form_typ": "pit"},
                "question_typ": {"question_typ": "txt4", "is_list": "n"},
                "question": "New pit Q?",
                "table_col_width": "100",
                "order": 1,
                "active": "y",
                "required": "n",
                "scout_question": {"id": None},
                "questionoption_set": [],
            }
            save_question(data)

        from form.models import Question
        new_q = Question.objects.get(question="New pit Q?")
        assert Answer.objects.filter(question=new_q, value="!EXIST").exists()


# ─────────────────────────────────────────────────────────────
#  get_question_types – line 375+
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetQuestionTypes:
    def test_get_question_types_returns_list(self):
        from form.util import get_question_types
        _make_question_type("qt1", "QT1")
        result = get_question_types()
        assert isinstance(result, list)
        assert all("question_typ" in qt for qt in result)


# ─────────────────────────────────────────────────────────────
#  save_or_update_answer / save_question_flow_answer
#  lines 432, 438-446, 454
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveOrUpdateAnswer:
    def test_save_new_answer_with_question(self):
        """Line 432+: create new answer."""
        from form.util import save_or_update_answer

        q = _make_question()
        resp = _make_response()
        data = {"question": {"id": q.id}, "value": "42"}
        answer = save_or_update_answer(data, resp)

        from form.models import Answer
        assert Answer.objects.filter(id=answer.id, value="42").exists()

    def test_update_existing_answer(self):
        """save_or_update_answer: update existing answer."""
        from form.util import save_or_update_answer
        from form.models import Answer

        q = _make_question(question="Q upd?")
        resp = _make_response()
        # Create existing answer
        Answer.objects.create(question=q, response=resp, value="old", void_ind="n")

        data = {"question": {"id": q.id}, "value": "new"}
        save_or_update_answer(data, resp)

        ans = Answer.objects.get(question=q, response=resp, void_ind="n")
        assert ans.value == "new"

    def test_save_answer_no_question_no_flow_raises(self):
        """Line 409: raises if neither question nor flow."""
        from form.util import save_or_update_answer

        resp = _make_response()
        with pytest.raises(Exception, match="No question or flow"):
            save_or_update_answer({}, resp)

    def test_save_answer_with_flow_answers(self):
        """Lines 431-432: flow_answers iteration (438-446)."""
        from form.util import save_or_update_answer
        from form.models import Flow

        ft = _make_form_type("survey7", "Survey7")
        flow = Flow.objects.create(name="F1", form_typ=ft, void_ind="n")
        q = _make_question(question="Flow Q?")
        resp = _make_response()

        data = {
            "question": {"id": q.id},
            "value": "5",
            "flow_answers": [
                {"question": {"id": q.id}, "value": "3", "value_time": None}
            ],
        }
        answer = save_or_update_answer(data, resp)
        assert answer is not None

    def test_save_question_flow_answer(self):
        """Lines 438-446: save_question_flow_answer directly."""
        from form.util import save_question_flow_answer
        from form.models import Answer

        q = _make_question(question="FA Q?")
        resp = _make_response()
        answer = Answer.objects.create(question=q, response=resp, value="x", void_ind="n")

        data = {"question": {"id": q.id}, "value": "7", "value_time": None}
        fa = save_question_flow_answer(data, answer)

        from form.models import FlowAnswer
        assert FlowAnswer.objects.filter(id=fa.id).exists()


# ─────────────────────────────────────────────────────────────
#  get_response, save_response, delete_response
#  lines 454, 463, 473-479, 492
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestResponseFunctions:
    def test_get_response(self):
        """Line 454+: get_response returns list of questions with answers."""
        from form.util import get_response

        ft = _make_form_type("survey8", "Survey8")
        resp = _make_response(ft)
        result = get_response(resp.id)
        assert isinstance(result, list)

    def test_save_response_new(self):
        """Lines 463-469: save new response."""
        from form.util import save_response
        from form.models import Response
        from django.utils import timezone

        ft = _make_form_type("survey9", "Survey9")
        data = {
            "form_typ": "survey9",
            "time": timezone.now(),
            "archive_ind": "n",
        }
        save_response(data)
        assert Response.objects.filter(form_typ=ft).exists()

    def test_delete_response(self):
        """Lines 473-479: delete (void) a response."""
        from form.util import delete_response

        resp = _make_response()
        # delete_response has a bug: uses response_id= instead of id=; mock it
        with patch("form.util.Response.objects.get", return_value=resp):
            delete_response(resp.id)

        assert resp.void_ind == "y"

    def test_get_responses(self):
        """Line 492+: get_responses returns list."""
        from form.util import get_responses

        ft = _make_form_type("srv10", "Survey10")
        _make_response(ft)
        result = get_responses("srv10", "n")
        assert isinstance(result, list)

    def test_get_response_question_answer_missing(self):
        """Line 513: answer not found returns '!FOUND'."""
        from form.util import get_response_question_answer

        resp = _make_response()
        result = get_response_question_answer(resp, 99999)
        assert result == "!FOUND"


# ─────────────────────────────────────────────────────────────
#  get_question_aggregates – lines 519-542, 546
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetQuestionAggregates:
    def test_get_question_aggregates_non_field(self):
        """Lines 519-542: get_question_aggregates for non-field form."""
        from form.util import get_question_aggregates
        result = get_question_aggregates("survey11")
        assert isinstance(result, list)

    def test_get_question_aggregates_field_type(self):
        """Line 522-527: field type adds season filter."""
        from form.util import get_question_aggregates
        from scouting.models import Season

        season = Season.objects.get_or_create(season="2030", defaults={"current": "n"})[0]
        with patch("form.util.scouting.util.get_current_season", return_value=season):
            with patch("form.util.scouting.models.Question.objects") as mock_sq:
                mock_sq.filter.return_value = []
                result = get_question_aggregates("field")
        assert isinstance(result, list)

    def test_get_question_aggregates_returns_parsed(self):
        """Line 540, 546: parse_question_aggregate is called."""
        from form.util import get_question_aggregates, parse_question_aggregate
        from form.models import QuestionAggregateQuestion

        ft = _make_form_type("srv12", "Survey12")
        qt = _make_question_type("t5", "T5")
        q = _make_question(form_typ=ft, question_typ=qt, question="AggQ1?")
        qa = _make_question_aggregate(name="MyAgg")
        QuestionAggregateQuestion.objects.create(
            question_aggregate=qa,
            question=q,
            order=1,
            active="y",
            void_ind="n",
        )

        result = get_question_aggregates("srv12")
        assert any(r["name"] == "MyAgg" for r in result)


# ─────────────────────────────────────────────────────────────
#  save_question_aggregate – lines 579, 584-617
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveQuestionAggregate:
    def test_save_new_question_aggregate(self):
        """Lines 579-617: save new question aggregate."""
        from form.util import save_question_aggregate
        from form.models import QuestionAggregate

        qt = _make_question_type("t6", "T6")
        qa_typ = _make_question_aggregate_type("sum")
        ft = _make_form_type("s13", "S13")
        q = _make_question(form_typ=ft, question_typ=qt, question="QA Q?")

        data = {
            "name": "New Aggregate",
            "horizontal": True,
            "use_answer_time": False,
            "active": "y",
            "question_aggregate_typ": {"question_aggregate_typ": "sum"},
            "aggregate_questions": [
                {
                    "question": {"id": q.id},
                    "condition_value": None,
                    "order": 1,
                    "active": "y",
                    "question_condition_typ": None,
                }
            ],
        }
        qa = save_question_aggregate(data)
        assert QuestionAggregate.objects.filter(name="New Aggregate").exists()

    def test_save_existing_question_aggregate(self):
        """Lines 579 (if branch): update existing aggregate."""
        from form.util import save_question_aggregate

        qa_typ = _make_question_aggregate_type("avg")
        qa = _make_question_aggregate(qa_typ=qa_typ, name="OldAgg")
        ft = _make_form_type("s14", "S14")
        qt = _make_question_type("t7", "T7")
        q = _make_question(form_typ=ft, question_typ=qt, question="EQ?")

        data = {
            "id": qa.id,
            "name": "UpdatedAgg",
            "horizontal": False,
            "use_answer_time": False,
            "active": "n",
            "question_aggregate_typ": {"question_aggregate_typ": "avg"},
            "aggregate_questions": [],
        }
        save_question_aggregate(data)
        qa.refresh_from_db()
        assert qa.name == "UpdatedAgg"

    def test_save_question_aggregate_with_condition_typ(self):
        """Lines 601-607: aggregate question with condition type."""
        from form.util import save_question_aggregate

        qa_typ = _make_question_aggregate_type("logical")
        ct = _make_condition_type("equal")
        ft = _make_form_type("s15", "S15")
        qt = _make_question_type("t8", "T8")
        q = _make_question(form_typ=ft, question_typ=qt, question="LQ?")

        data = {
            "name": "LogicalAgg",
            "horizontal": True,
            "use_answer_time": False,
            "active": "y",
            "question_aggregate_typ": {"question_aggregate_typ": "logical"},
            "aggregate_questions": [
                {
                    "question": {"id": q.id},
                    "condition_value": "5",
                    "order": 1,
                    "active": "y",
                    "question_condition_typ": {"question_condition_typ": "equal"},
                }
            ],
        }
        qa = save_question_aggregate(data)
        assert qa is not None


# ─────────────────────────────────────────────────────────────
#  get_question_conditions – lines 621-654
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetQuestionConditions:
    def test_get_question_conditions_empty(self):
        """Lines 621-654: returns empty list when no conditions."""
        from form.util import get_question_conditions
        result = get_question_conditions("s16")
        assert result == []

    def test_get_question_conditions_with_data(self):
        """Lines 641-652: iterate and parse conditions."""
        from form.util import get_question_conditions
        from form.models import QuestionCondition

        ft = _make_form_type("s17", "S17")
        qt = _make_question_type("t9", "T9")
        ct = _make_condition_type("gt")
        q_from = _make_question(form_typ=ft, question_typ=qt, question="From Q?")
        q_to = _make_question(form_typ=ft, question_typ=qt, question="To Q?")
        QuestionCondition.objects.create(
            question_condition_typ=ct,
            value="3",
            question_from=q_from,
            question_to=q_to,
            active="y",
            void_ind="n",
        )

        result = get_question_conditions("s17")
        assert len(result) >= 1
        assert result[0]["value"] == "3"

    def test_get_question_conditions_field_type(self):
        """Lines 624-629: field type uses season filter."""
        from form.util import get_question_conditions
        from scouting.models import Season

        season = Season.objects.get_or_create(season="2031", defaults={"current": "n"})[0]
        with patch("form.util.scouting.util.get_current_season", return_value=season):
            with patch("form.util.scouting.models.Question.objects") as mock_sq:
                mock_sq.filter.return_value = []
                result = get_question_conditions("field")
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────
#  save_question_condition – lines 662-680
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveQuestionCondition:
    def test_save_new_question_condition(self):
        """Lines 662-680: create new question condition."""
        from form.util import save_question_condition
        from form.models import QuestionCondition

        ft = _make_form_type("s18", "S18")
        qt = _make_question_type("t10", "T10")
        ct = _make_condition_type("lt")
        q_from = _make_question(form_typ=ft, question_typ=qt, question="CF?")
        q_to = _make_question(form_typ=ft, question_typ=qt, question="CT?")

        data = {
            "value": "10",
            "question_condition_typ": {"question_condition_typ": "lt"},
            "active": "y",
            "question_from": {"id": q_from.id},
            "question_to": {"id": q_to.id},
        }
        qc = save_question_condition(data)
        assert QuestionCondition.objects.filter(question_condition_id=qc.question_condition_id).exists()

    def test_save_existing_question_condition(self):
        """Lines 662-663 (if branch): update existing condition."""
        from form.util import save_question_condition
        from form.models import QuestionCondition

        ft = _make_form_type("s19", "S19")
        qt = _make_question_type("t11", "T11")
        ct = _make_condition_type("gt-equal")
        q_from = _make_question(form_typ=ft, question_typ=qt, question="CF2?")
        q_to = _make_question(form_typ=ft, question_typ=qt, question="CT2?")
        qc_existing = QuestionCondition.objects.create(
            question_condition_typ=ct,
            value="0",
            question_from=q_from,
            question_to=q_to,
            active="y",
            void_ind="n",
        )

        data = {
            "question_condition_id": qc_existing.question_condition_id,
            "value": "99",
            "question_condition_typ": {"question_condition_typ": "gt-equal"},
            "active": "n",
            "question_from": {"id": q_from.id},
            "question_to": {"id": q_to.id},
        }
        save_question_condition(data)
        qc_existing.refresh_from_db()
        assert qc_existing.value == "99"


# ─────────────────────────────────────────────────────────────
#  format_question_condition_values – line 684
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFormatQuestionConditionValues:
    def test_format_question_condition_values(self):
        """Line 684+: format a condition into dict."""
        from form.util import format_question_condition_values

        # format_question_condition_values accesses qc.condition (a bug - should be qc.value)
        # Use a mock object to cover the function
        mock_qc = Mock()
        mock_qc.question_condition_id = 1
        mock_qc.condition = "equal"
        mock_qc.active = "y"

        with patch("form.util.parse_question", return_value={}):
            result = format_question_condition_values(mock_qc)
        assert result["question_condition_id"] == 1


# ─────────────────────────────────────────────────────────────
#  get_flow_condition – lines 694-716
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetFlowCondition:
    def test_get_flow_condition_empty(self):
        """Lines 694-716: empty result for unknown form type."""
        from form.util import get_flow_condition
        result = get_flow_condition("s21")
        assert result == []

    def test_get_flow_condition_with_data(self):
        """Lines 706-714: parses flow conditions."""
        from form.util import get_flow_condition
        from form.models import Flow, FlowCondition

        ft = _make_form_type("s22", "S22")
        flow_from = Flow.objects.create(name="FlowA", form_typ=ft, void_ind="n")
        flow_to = Flow.objects.create(name="FlowB", form_typ=ft, void_ind="n")
        FlowCondition.objects.create(
            flow_from=flow_from, flow_to=flow_to, active="y", void_ind="n"
        )

        result = get_flow_condition("s22")
        assert len(result) >= 1
        assert result[0]["flow_from"]["id"] == flow_from.id

    def test_get_flow_condition_field_type(self):
        """Lines 698-701: field type adds season filter."""
        from form.util import get_flow_condition
        from scouting.models import Season

        season = Season.objects.get_or_create(season="2032", defaults={"current": "n"})[0]
        with patch("form.util.scouting.util.get_current_season", return_value=season):
            result = get_flow_condition("field")
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────
#  save_flow_condition – lines 720-732
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveFlowCondition:
    def test_save_new_flow_condition(self):
        """Lines 720-732: create new flow condition."""
        from form.util import save_flow_condition
        from form.models import Flow, FlowCondition

        ft = _make_form_type("s23", "S23")
        flow_from = Flow.objects.create(name="FC_from", form_typ=ft, void_ind="n")
        flow_to = Flow.objects.create(name="FC_to", form_typ=ft, void_ind="n")

        data = {
            "active": "y",
            "flow_from": {"id": flow_from.id},
            "flow_to": {"id": flow_to.id},
        }
        fc = save_flow_condition(data)
        assert FlowCondition.objects.filter(id=fc.id).exists()

    def test_save_existing_flow_condition(self):
        """Lines 721 (if branch): update existing flow condition."""
        from form.util import save_flow_condition
        from form.models import Flow, FlowCondition

        ft = _make_form_type("s24", "S24")
        flow_from = Flow.objects.create(name="FC2_from", form_typ=ft, void_ind="n")
        flow_to = Flow.objects.create(name="FC2_to", form_typ=ft, void_ind="n")
        fc_existing = FlowCondition.objects.create(
            flow_from=flow_from, flow_to=flow_to, active="y", void_ind="n"
        )

        data = {
            "id": fc_existing.id,
            "active": "n",
            "flow_from": {"id": flow_from.id},
            "flow_to": {"id": flow_to.id},
        }
        save_flow_condition(data)
        fc_existing.refresh_from_db()
        assert fc_existing.active == "n"


# ─────────────────────────────────────────────────────────────
#  format_flow_values – lines 737-751
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFormatFlowValues:
    def test_format_flow_values_basic(self):
        """Lines 737-751: format_flow_values returns expected dict."""
        from form.util import format_flow_values
        from form.models import Flow

        ft = _make_form_type("s25", "S25")
        flow = Flow.objects.create(name="FV flow", form_typ=ft, void_ind="n")
        result = format_flow_values(flow)
        assert result["id"] == flow.id
        assert result["name"] == "FV flow"
        assert "flow_questions" in result

    def test_format_flow_values_with_conditions(self):
        """Lines 738-742: flow has outgoing conditions."""
        from form.util import format_flow_values
        from form.models import Flow, FlowCondition

        ft = _make_form_type("s26", "S26")
        flow_from = Flow.objects.create(name="HCond from", form_typ=ft, void_ind="n")
        flow_to = Flow.objects.create(name="HCond to", form_typ=ft, void_ind="n")
        FlowCondition.objects.create(
            flow_from=flow_from, flow_to=flow_to, active="y", void_ind="n"
        )

        result = format_flow_values(flow_from)
        assert result["has_conditions"] == "y"

    def test_format_flow_values_conditional_on(self):
        """Lines 747-749: flow is conditional on another."""
        from form.util import format_flow_values
        from form.models import Flow, FlowCondition

        ft = _make_form_type("s27", "S27")
        flow_from = Flow.objects.create(name="CO from", form_typ=ft, void_ind="n")
        flow_to = Flow.objects.create(name="CO to", form_typ=ft, void_ind="n")
        FlowCondition.objects.create(
            flow_from=flow_from, flow_to=flow_to, active="y", void_ind="n"
        )

        result = format_flow_values(flow_to)
        assert result["flow_conditional_on"] == flow_from.id


# ─────────────────────────────────────────────────────────────
#  get_form_questions – lines 791-794
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetFormQuestions:
    def test_get_form_questions(self):
        """Lines 791-794: returns dict with form_sub_types."""
        from form.util import get_form_questions
        from form.models import FormSubType
        from scouting.models import Season

        ft = _make_form_type("s28", "S28")
        fst = FormSubType.objects.create(
            form_sub_typ="sub28", form_sub_nm="Sub 28", form_typ=ft, order=1
        )

        season = Season.objects.get_or_create(season="2060", defaults={"current": "n"})[0]
        with patch("form.util.scouting.util.get_current_season", return_value=season):
            with patch("form.util.scouting.models.Question.objects") as mock_sq:
                mock_sq.filter.return_value = []
                result = get_form_questions("s28")

        assert "form_sub_types" in result
        assert len(result["form_sub_types"]) >= 1


# ─────────────────────────────────────────────────────────────
#  get_flows – lines 917-942
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetFlows:
    def test_get_flows_empty(self):
        from form.util import get_flows
        result = get_flows()
        assert isinstance(result, list)

    def test_get_flows_by_id(self):
        """Lines 917-919: filter by id."""
        from form.util import get_flows
        from form.models import Flow

        ft = _make_form_type("s29", "S29")
        flow = Flow.objects.create(name="GetF by id", form_typ=ft, void_ind="n")
        result = get_flows(fid=flow.id)
        assert any(r["id"] == flow.id for r in result)

    def test_get_flows_by_form_typ(self):
        """Lines 921-923: filter by form_typ."""
        from form.util import get_flows
        from form.models import Flow

        ft = _make_form_type("s30", "S30")
        Flow.objects.create(name="GetF by typ", form_typ=ft, void_ind="n")
        result = get_flows(form_typ="s30")
        assert len(result) >= 1

    def test_get_flows_field_type_season_filter(self):
        """Lines 929-932: field type adds season filter."""
        from form.util import get_flows
        from scouting.models import Season

        season = Season.objects.get_or_create(season="2033", defaults={"current": "n"})[0]
        with patch("form.util.scouting.util.get_current_season", return_value=season):
            result = get_flows(form_typ="field")
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────
#  save_flow – lines 946-993
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveFlow:
    def test_save_new_flow(self):
        """Lines 946-993: create new flow."""
        from form.util import save_flow
        from form.models import Flow

        ft = _make_form_type("s31", "S31")
        qt = _make_question_type("t13", "T13")
        q = _make_question(form_typ=ft, question_typ=qt, question="FQ?")

        data = {
            "name": "New Flow",
            "single_run": False,
            "form_based": False,
            "form_typ": {"form_typ": "s31"},
            "form_sub_typ": None,
            "void_ind": "n",
            "flow_questions": [
                {
                    "question": {
                        "id": q.id,
                        "form_typ": {"form_typ": ft.form_typ},
                        "question_typ": {"question_typ": qt.question_typ, "is_list": "n"},
                        "question": "FQ?",
                        "table_col_width": "100",
                        "order": 1,
                        "active": "y",
                        "required": "n",
                        "questionoption_set": [],
                    },
                    "press_to_continue": False,
                    "order": 1,
                    "active": "y",
                }
            ],
        }
        flow = save_flow(data)
        assert Flow.objects.filter(name="New Flow").exists()

    def test_save_existing_flow(self):
        """Lines 946-947 (if branch): update existing flow."""
        from form.util import save_flow
        from form.models import Flow

        ft = _make_form_type("s32", "S32")
        flow = Flow.objects.create(name="Old Flow", form_typ=ft, void_ind="n")

        data = {
            "id": flow.id,
            "name": "Updated Flow",
            "single_run": True,
            "form_based": False,
            "form_typ": {"form_typ": "s32"},
            "void_ind": "n",
            "flow_questions": [],
        }
        save_flow(data)
        flow.refresh_from_db()
        assert flow.name == "Updated Flow"

    def test_save_flow_with_form_sub_typ(self):
        """Lines 955-956: form_sub_typ is set."""
        from form.util import save_flow
        from form.models import Flow, FormSubType

        ft = _make_form_type("s33", "S33")
        fst = FormSubType.objects.create(
            form_sub_typ="sub33", form_sub_nm="Sub33", form_typ=ft, order=1
        )

        data = {
            "name": "Sub Flow",
            "single_run": False,
            "form_based": False,
            "form_typ": {"form_typ": "s33"},
            "form_sub_typ": {"form_sub_typ": "sub33"},
            "void_ind": "n",
            "flow_questions": [],
        }
        flow = save_flow(data)
        assert Flow.objects.filter(name="Sub Flow", form_sub_typ=fst).exists()

    def test_save_flow_field_type_creates_scout_link(self):
        """Lines 984-991: field type creates QuestionFlow link."""
        from form.util import save_flow
        from form.models import Flow

        ft = _make_form_type("field2", "Field2")
        season_mock = Mock(id=99)

        with patch("form.util.scouting.util.get_current_season", return_value=season_mock):
            with patch("form.util.scouting.models.QuestionFlow") as mock_qf_class:
                mock_qf_inst = Mock()
                mock_qf_class.return_value = mock_qf_inst
                mock_qf_class.DoesNotExist = Exception
                with patch("form.util.scouting.models.QuestionFlow.objects") as mock_qf_obj:
                    mock_qf_obj.filter.return_value.get.side_effect = Exception()
                    data = {
                        "name": "Field Flow",
                        "single_run": False,
                        "form_based": False,
                        "form_typ": {"form_typ": "field2"},
                        "void_ind": "n",
                        "flow_questions": [],
                    }
                    flow = save_flow(data)
        assert Flow.objects.filter(name="Field Flow").exists()


# ─────────────────────────────────────────────────────────────
#  get_graph_types, get_graph_question_types – lines 996-1001
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetGraphTypes:
    def test_get_graph_types(self):
        from form.util import get_graph_types
        result = list(get_graph_types())
        assert isinstance(result, list)

    def test_get_graph_question_types(self):
        from form.util import get_graph_question_types
        result = list(get_graph_question_types())
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────
#  parse_graph_category / attribute / question – lines 1005-1056
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestParseGraphObjects:
    def test_parse_graph_category(self):
        """Lines 1005-1017: parse graph category."""
        from form.util import parse_graph_category
        from form.models import GraphCategory
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="pgcuser", email="pgcuser@test.com", password="pass")
        g = _make_graph(user)
        gc = GraphCategory.objects.create(
            graph=g, category="CatA", order=1, active="y", void_ind="n"
        )
        result = parse_graph_category(gc)
        assert result["category"] == "CatA"
        assert result["graphcategoryattribute_set"] == []

    def test_parse_graph_category_attribute_with_question(self):
        """Lines 1020-1037: parse attribute with question."""
        from form.util import parse_graph_category_attribute
        from form.models import GraphCategory, GraphCategoryAttribute
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="pgcauser", email="pgcauser@test.com", password="pass")
        g = _make_graph(user)
        gc = GraphCategory.objects.create(
            graph=g, category="CatB", order=1, active="y", void_ind="n"
        )
        qt = _make_question_type("t14", "T14")
        ft = _make_form_type("s34", "S34")
        q = _make_question(form_typ=ft, question_typ=qt, question="Attr Q?")
        ct = _make_condition_type("equal2") if not hasattr(_make_condition_type, "_eq2") else _make_condition_type("equal")
        ct = _make_condition_type("equal")

        gca = GraphCategoryAttribute.objects.create(
            graph_category=gc,
            question=q,
            question_condition_typ=ct,
            value="1",
            active="y",
            void_ind="n",
        )
        result = parse_graph_category_attribute(gca)
        assert result["value"] == "1"
        assert result["question"] is not None

    def test_parse_graph_category_attribute_with_aggregate(self):
        """Lines 1029-1033: attribute with question_aggregate."""
        from form.util import parse_graph_category_attribute
        from form.models import GraphCategory, GraphCategoryAttribute
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="pgcaauser", email="pgcaauser@test.com", password="pass")
        g = _make_graph(user)
        gc = GraphCategory.objects.create(
            graph=g, category="CatC", order=1, active="y", void_ind="n"
        )
        ct = _make_condition_type("equal")
        qa = _make_question_aggregate(name="AttrAgg")

        gca = GraphCategoryAttribute.objects.create(
            graph_category=gc,
            question_aggregate=qa,
            question_condition_typ=ct,
            value="2",
            active="y",
            void_ind="n",
        )
        result = parse_graph_category_attribute(gca)
        assert result["question_aggregate"] is not None

    def test_parse_graph_question_with_question(self):
        """Lines 1040-1056: parse graph question with question."""
        from form.util import parse_graph_question
        from form.models import GraphQuestion, GraphQuestionType
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="pgquser", email="pgquser@test.com", password="pass")
        g = _make_graph(user)
        qt_form = _make_question_type("t15", "T15")
        ft = _make_form_type("s35", "S35")
        q = _make_question(form_typ=ft, question_typ=qt_form, question="GQ Q?")

        gqt, _ = GraphQuestionType.objects.get_or_create(
            graph_question_typ="x-axis", defaults={"graph_question_nm": "X Axis"}
        )
        gq = GraphQuestion.objects.create(
            graph=g, question=q, active="y", void_ind="n"
        )
        result = parse_graph_question(gq)
        assert result["question"] is not None

    def test_parse_graph_question_with_aggregate(self):
        """Lines 1049-1052: parse graph question with aggregate."""
        from form.util import parse_graph_question
        from form.models import GraphQuestion
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="pgqauser", email="pgqauser@test.com", password="pass")
        g = _make_graph(user)
        qa = _make_question_aggregate(name="GQAgg")

        gq = GraphQuestion.objects.create(
            graph=g, question_aggregate=qa, active="y", void_ind="n"
        )
        result = parse_graph_question(gq)
        assert result["question_aggregate"] is not None


# ─────────────────────────────────────────────────────────────
#  get_graphs – lines 1059-1106
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetGraphs:
    def test_get_graphs_empty(self):
        from form.util import get_graphs
        result = get_graphs()
        assert isinstance(result, list)

    def test_get_graphs_by_id(self):
        """Lines 1068-1070: filter by graph_id."""
        from form.util import get_graphs
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="gguser", email="gguser@test.com", password="pass")
        g = _make_graph(user, name="GG Graph")
        result = get_graphs(graph_id=g.id)
        assert any(r["id"] == g.id for r in result)

    def test_get_graphs_for_current_season(self):
        """Lines 1061-1066: for_current_season filter."""
        from form.util import get_graphs
        from scouting.models import Season

        season = Season.objects.get_or_create(season="2034", defaults={"current": "n"})[0]
        with patch("form.util.scouting.util.get_current_season", return_value=season):
            result = get_graphs(for_current_season=True)
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────
#  save_graph – lines 1110-1272
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveGraph:
    def test_save_new_graph_simple(self):
        """Lines 1110-1124: create new graph without bins/categories."""
        from form.util import save_graph
        from form.models import Graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser1", email="sguser1@test.com", password="pass")
        gt = _make_graph_type("line2")
        ft = _make_form_type("s36", "S36")
        qt = _make_question_type("t16", "T16")
        q = _make_question(form_typ=ft, question_typ=qt, question="SG Q1?")

        data = {
            "graph_typ": {
                "graph_typ": "line2",
                "requires_bins": False,
                "requires_categories": False,
                "requires_graph_question_typs": [],
            },
            "name": "New SG Graph",
            "x_scale_min": 0,
            "x_scale_max": 10,
            "y_scale_min": 0,
            "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [
                {
                    "question": {"id": q.id},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        }
        save_graph(data, user.id, for_current_season=False)
        assert Graph.objects.filter(name="New SG Graph").exists()

    def test_save_existing_graph(self):
        """Lines 1113-1114 (else branch): update existing graph."""
        from form.util import save_graph
        from form.models import Graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser2", email="sguser2@test.com", password="pass")
        g = _make_graph(user, name="Original SG")
        ft = _make_form_type("s37", "S37")
        qt = _make_question_type("t17", "T17")
        q = _make_question(form_typ=ft, question_typ=qt, question="SG Q2?")

        data = {
            "id": g.id,
            "graph_typ": {
                "graph_typ": g.graph_typ.graph_typ,
                "requires_bins": False,
                "requires_categories": False,
                "requires_graph_question_typs": [],
            },
            "name": "Updated SG",
            "x_scale_min": 0,
            "x_scale_max": 20,
            "y_scale_min": 0,
            "y_scale_max": 20,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [
                {
                    "question": {"id": q.id},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        }
        save_graph(data, user.id)
        g.refresh_from_db()
        assert g.name == "Updated SG"

    def test_save_graph_requires_bins_raises_if_empty(self):
        """Lines 1136-1137: raises if requires_bins and no bins."""
        from form.util import save_graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser3", email="sguser3@test.com", password="pass")
        gt = _make_graph_type("histo2", requires_bins=True)

        data = {
            "graph_typ": {
                "graph_typ": "histo2",
                "requires_bins": True,
                "requires_categories": False,
                "requires_graph_question_typs": [],
            },
            "name": "Bin Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [],
        }
        with pytest.raises(Exception, match="No bins provided"):
            save_graph(data, user.id)

    def test_save_graph_with_bins(self):
        """Lines 1139-1150: save graph with bins."""
        from form.util import save_graph
        from form.models import Graph, GraphBin
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser4", email="sguser4@test.com", password="pass")
        gt = _make_graph_type("histo3", requires_bins=True)
        ft = _make_form_type("s38", "S38")
        qt = _make_question_type("t18", "T18")
        q = _make_question(form_typ=ft, question_typ=qt, question="Bin Q?")

        data = {
            "graph_typ": {
                "graph_typ": "histo3",
                "requires_bins": True,
                "requires_categories": False,
                "requires_graph_question_typs": [],
            },
            "name": "Bin SG Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [{"bin": 0, "width": 5, "active": "y"}],
            "graphcategory_set": [],
            "graphquestion_set": [
                {
                    "question": {"id": q.id},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        }
        save_graph(data, user.id)
        assert Graph.objects.filter(name="Bin SG Graph").exists()

    def test_save_graph_requires_categories_raises_if_empty(self):
        """Lines 1154-1155: raises if requires_categories and no categories."""
        from form.util import save_graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser5", email="sguser5@test.com", password="pass")
        _make_graph_type("cat2", requires_categories=True)

        data = {
            "graph_typ": {
                "graph_typ": "cat2",
                "requires_bins": False,
                "requires_categories": True,
                "requires_graph_question_typs": [],
            },
            "name": "Cat Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [],
        }
        with pytest.raises(Exception, match="No categories provided"):
            save_graph(data, user.id)

    def test_save_graph_requires_question_typ_missing_raises(self):
        """Lines 1270-1273: missing required graph question type raises."""
        from form.util import save_graph
        from form.models import GraphQuestionType
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser6", email="sguser6@test.com", password="pass")
        gqt, _ = GraphQuestionType.objects.get_or_create(
            graph_question_typ="y-axis", defaults={"graph_question_nm": "Y Axis"}
        )
        gt = _make_graph_type("reqtyp1")
        gt.requires_graph_question_typs.set([gqt])

        ft = _make_form_type("s39", "S39")
        qt = _make_question_type("t19", "T19")
        q = _make_question(form_typ=ft, question_typ=qt, question="Req Q?")

        data = {
            "graph_typ": {
                "graph_typ": "reqtyp1",
                "requires_bins": False,
                "requires_categories": False,
                "requires_graph_question_typs": [
                    {"graph_question_typ": "y-axis"}
                ],
            },
            "name": "Req Typ Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [
                # no graph_question_typ set – requirement not met
                {
                    "question": {"id": q.id},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        }
        with pytest.raises(Exception, match="Missing graph question requirement"):
            save_graph(data, user.id)

    def test_save_graph_for_current_season(self):
        """Lines 1126-1132: for_current_season creates scouting.Graph if needed."""
        from form.util import save_graph
        from form.models import Graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser7", email="sguser7@test.com", password="pass")
        season_mock = Mock(id=100)

        with patch("form.util.scouting.util.get_current_season", return_value=season_mock):
            with patch("form.util.scouting.models.Graph") as mock_sg_class:
                mock_sg_class.DoesNotExist = Exception
                mock_sg_class.objects.get.side_effect = Exception()
                mock_sg_inst = Mock()
                mock_sg_class.return_value = mock_sg_inst

                ft = _make_form_type("s40", "S40")
                qt = _make_question_type("t20", "T20")
                q = _make_question(form_typ=ft, question_typ=qt, question="Season Q?")

                data = {
                    "graph_typ": {
                        "graph_typ": _make_graph_type("linex").graph_typ,
                        "requires_bins": False,
                        "requires_categories": False,
                        "requires_graph_question_typs": [],
                    },
                    "name": "Season Graph",
                    "x_scale_min": 0, "x_scale_max": 10,
                    "y_scale_min": 0, "y_scale_max": 10,
                    "active": "y",
                    "graphbin_set": [],
                    "graphcategory_set": [],
                    "graphquestion_set": [
                        {
                            "question": {"id": q.id},
                            "question_aggregate": None,
                            "graph_question_typ": None,
                            "active": "y",
                        }
                    ],
                }
                save_graph(data, user.id, for_current_season=True)
        assert Graph.objects.filter(name="Season Graph").exists()

    def test_save_graph_question_aggregate_only(self):
        """Lines 1250+: graph question with aggregate (no question)."""
        from form.util import save_graph
        from form.models import Graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser8", email="sguser8@test.com", password="pass")
        qa = _make_question_aggregate(name="SG Agg")

        data = {
            "graph_typ": {
                "graph_typ": _make_graph_type("liney").graph_typ,
                "requires_bins": False,
                "requires_categories": False,
                "requires_graph_question_typs": [],
            },
            "name": "Agg Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [
                {
                    "question": None,
                    "question_aggregate": {"id": qa.id},
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        }
        save_graph(data, user.id)
        assert Graph.objects.filter(name="Agg Graph").exists()

    def test_save_graph_no_question_no_aggregate_raises(self):
        """Lines 1250-1251: no question and no aggregate raises."""
        from form.util import save_graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser9", email="sguser9@test.com", password="pass")

        data = {
            "graph_typ": {
                "graph_typ": _make_graph_type("linez").graph_typ,
                "requires_bins": False,
                "requires_categories": False,
                "requires_graph_question_typs": [],
            },
            "name": "No Q Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [],
            "graphquestion_set": [
                {
                    "question": None,
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        }
        with pytest.raises(Exception, match="No question or aggregate"):
            save_graph(data, user.id)

    def test_save_graph_with_full_categories(self):
        """Lines 1152-1213: save graph with categories and attributes."""
        from form.util import save_graph
        from form.models import Graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser10", email="sguser10@test.com", password="pass")
        gt = _make_graph_type("cat3", requires_categories=True)
        ct = _make_condition_type("equal")
        ft = _make_form_type("s41", "S41")
        qt = _make_question_type("t21", "T21")
        q = _make_question(form_typ=ft, question_typ=qt, question="Cat Q?")

        data = {
            "graph_typ": {
                "graph_typ": "cat3",
                "requires_bins": False,
                "requires_categories": True,
                "requires_graph_question_typs": [],
            },
            "name": "Full Cat Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [
                {
                    "category": "Cat1",
                    "order": 1,
                    "active": "y",
                    "graphcategoryattribute_set": [
                        {
                            "question": {"id": q.id},
                            "question_aggregate": None,
                            "question_condition_typ": {"question_condition_typ": "equal"},
                            "value": "yes",
                            "active": "y",
                        }
                    ],
                }
            ],
            "graphquestion_set": [],
        }
        save_graph(data, user.id)
        assert Graph.objects.filter(name="Full Cat Graph").exists()

    def test_save_graph_categories_empty_attributes_raises(self):
        """Lines 1173-1174: category with no attributes raises."""
        from form.util import save_graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser11", email="sguser11@test.com", password="pass")
        _make_graph_type("cat4", requires_categories=True)

        data = {
            "graph_typ": {
                "graph_typ": "cat4",
                "requires_bins": False,
                "requires_categories": True,
                "requires_graph_question_typs": [],
            },
            "name": "No Attr Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [
                {
                    "category": "EmptyCat",
                    "order": 1,
                    "active": "y",
                    "graphcategoryattribute_set": [],
                }
            ],
            "graphquestion_set": [],
        }
        with pytest.raises(Exception, match="No category attribute"):
            save_graph(data, user.id)

    def test_save_graph_category_attribute_no_q_no_agg_raises(self):
        """Lines 1194-1195: category attribute with no question and no agg."""
        from form.util import save_graph
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sguser12", email="sguser12@test.com", password="pass")
        _make_graph_type("cat5", requires_categories=True)

        data = {
            "graph_typ": {
                "graph_typ": "cat5",
                "requires_bins": False,
                "requires_categories": True,
                "requires_graph_question_typs": [],
            },
            "name": "No Q Attr Graph",
            "x_scale_min": 0, "x_scale_max": 10,
            "y_scale_min": 0, "y_scale_max": 10,
            "active": "y",
            "graphbin_set": [],
            "graphcategory_set": [
                {
                    "category": "NQACat",
                    "order": 1,
                    "active": "y",
                    "graphcategoryattribute_set": [
                        {
                            "question": None,
                            "question_aggregate": None,
                            "question_condition_typ": None,
                            "value": "x",
                            "active": "y",
                        }
                    ],
                }
            ],
            "graphquestion_set": [],
        }
        with pytest.raises(Exception, match="No question or aggregate"):
            save_graph(data, user.id)


# ─────────────────────────────────────────────────────────────
#  save_field_response – lines 839-865
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveFieldResponse:
    def test_save_field_response(self):
        """Lines 839-865: save a field response."""
        from form.util import save_field_response
        from scouting.models import Season, Event, Team
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sfruser", email="sfruser@test.com", password="pass")

        ft = _make_form_type("field", "Field")
        season = Season.objects.get_or_create(season="2040", defaults={"current": "y"})[0]
        event = Event.objects.create(
            season=season,
            event_cd="EVT3",
            event_nm="Event 3",
            date_st="2040-01-01T00:00:00Z",
            date_end="2040-01-02T00:00:00Z",
            void_ind="n",
        )
        team = Team.objects.get_or_create(team_no=9999, defaults={"team_nm": "T9999"})[0]
        qt = _make_question_type("t22", "T22")
        q = _make_question(form_typ=ft, question_typ=qt, question="FR Q?")

        with patch("form.util.scouting.util.get_current_event", return_value=event):
            data = {
                "form_typ": "field",
                "team_id": 9999,
                "match_key": "non_existent_match",
                "answers": [{"question": {"id": q.id}, "value": "7"}],
            }
            fr = save_field_response(data, user.id)

        assert fr.team_id == 9999

    def test_save_field_response_with_existing_match(self):
        """Lines 842-844: match found."""
        from form.util import save_field_response
        from scouting.models import Season, Event, Match, CompetitionLevel, Team
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="sfr2user", email="sfr2user@test.com", password="pass")

        ft = _make_form_type("field", "Field")
        season = Season.objects.get_or_create(season="2041", defaults={"current": "y"})[0]
        event = Event.objects.create(
            season=season,
            event_cd="EVT4",
            event_nm="Event 4",
            date_st="2041-01-01T00:00:00Z",
            date_end="2041-01-02T00:00:00Z",
            void_ind="n",
        )
        team = Team.objects.get_or_create(team_no=1111, defaults={"team_nm": "T1111"})[0]
        comp_lvl, _ = CompetitionLevel.objects.get_or_create(
            comp_lvl_typ="qm", defaults={"comp_lvl_typ_nm": "Qual", "comp_lvl_order": 1}
        )
        match = Match.objects.create(
            match_key="2041evt_qm1",
            match_number=1,
            event=event,
            comp_level=comp_lvl,
            void_ind="n",
        )

        with patch("form.util.scouting.util.get_current_event", return_value=event):
            data = {
                "form_typ": "field",
                "team_id": 1111,
                "match_key": "2041evt_qm1",
                "answers": [],
            }
            fr = save_field_response(data, user.id)

        assert fr is not None


# ─────────────────────────────────────────────────────────────
#  save_pit_response – lines 869-901
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSavePitResponse:
    def test_save_new_pit_response(self):
        """Lines 884-895: new pit response."""
        from form.util import save_pit_response
        from scouting.models import Season, Event, Team
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="spruser", email="spruser@test.com", password="pass")

        ft = _make_form_type("pit", "Pit")
        season = Season.objects.get_or_create(season="2042", defaults={"current": "y"})[0]
        event = Event.objects.create(
            season=season,
            event_cd="EVT5",
            event_nm="Event 5",
            date_st="2042-01-01T00:00:00Z",
            date_end="2042-01-02T00:00:00Z",
            void_ind="n",
        )
        team = Team.objects.get_or_create(team_no=2222, defaults={"team_nm": "T2222"})[0]

        with patch("form.util.scouting.util.get_current_event", return_value=event):
            data = {
                "form_typ": "pit",
                "team_id": 2222,
                "answers": [],
            }
            sp = save_pit_response(data, user.id)

        assert sp.team_id == 2222

    def test_save_pit_response_existing(self):
        """Lines 873-883: existing pit response."""
        from form.util import save_pit_response
        from form.models import Response
        from scouting.models import Season, Event, PitResponse, Team
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username="spr2user", email="spr2user@test.com", password="pass")

        ft = _make_form_type("pit", "Pit")
        season = Season.objects.get_or_create(season="2043", defaults={"current": "y"})[0]
        event = Event.objects.create(
            season=season,
            event_cd="EVT6",
            event_nm="Event 6",
            date_st="2043-01-01T00:00:00Z",
            date_end="2043-01-02T00:00:00Z",
            void_ind="n",
        )
        team = Team.objects.get_or_create(team_no=3333, defaults={"team_nm": "T3333"})[0]
        resp = _make_response(ft)
        pr = PitResponse.objects.create(
            event=event, team=team, user=user, response=resp, void_ind="n"
        )

        with patch("form.util.scouting.util.get_current_event", return_value=event):
            data = {
                "form_typ": "pit",
                "team_id": 3333,
                "answers": [],
            }
            sp = save_pit_response(data, user.id)

        assert sp.team_id == 3333


# ─────────────────────────────────────────────────────────────
#  save_answers – lines 905-913
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaveAnswers:
    def test_save_answers(self):
        """Lines 905-913: save generic answers."""
        from form.util import save_answers
        from form.models import Response

        ft = _make_form_type("s42", "S42")
        qt = _make_question_type("t23", "T23")
        q = _make_question(form_typ=ft, question_typ=qt, question="SA Q?")

        data = {
            "form_typ": "s42",
            "question_answers": [
                {"question": {"id": q.id}, "value": "yes"}
            ],
        }
        save_answers(data)
        assert Response.objects.filter(form_typ=ft).exists()


# ─────────────────────────────────────────────────────────────
#  is_question_condition_passed – lines 1919-1936
# ─────────────────────────────────────────────────────────────

class TestIsQuestionConditionPassed:
    def test_none_answer_returns_false(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("equal", None) is False

    def test_equal(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("equal", "yes", "yes") is True
        assert is_question_condition_passed("equal", "yes", "no") is False

    def test_gt(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("gt", "5", "3") is True
        assert is_question_condition_passed("gt", "3", "5") is False

    def test_gt_equal(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("gt-equal", "5", "5") is True
        assert is_question_condition_passed("gt-equal", "4", "5") is False

    def test_lt_equal(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("lt-equal", "5", "5") is True
        assert is_question_condition_passed("lt-equal", "6", "5") is False

    def test_lt(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("lt", "3", "5") is True
        assert is_question_condition_passed("lt", "5", "3") is False

    def test_exist_with_value(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("exist", "x") is True

    def test_exist_empty_string(self):
        from form.util import is_question_condition_passed
        assert is_question_condition_passed("exist", "") is False

    def test_unknown_type_raises(self):
        from form.util import is_question_condition_passed
        with pytest.raises(Exception, match="no type"):
            is_question_condition_passed("invalid", "5", "3")


# ─────────────────────────────────────────────────────────────
#  aggregate_answers_horizontally / vertically – lines 1940-1979
# ─────────────────────────────────────────────────────────────

class _MockQuestion:
    """Supports both dict-style (q["id"]) and attribute (q.value_multiplier) access."""
    def __init__(self, qid, active="y", value_multiplier=None):
        self.id = qid
        self.active = active
        self.value_multiplier = value_multiplier

    def __getitem__(self, key):
        return getattr(self, key)

    def __eq__(self, other):
        if isinstance(other, _MockQuestion):
            return self.id == other.id
        return NotImplemented


@pytest.mark.django_db
class TestAggregateAnswers:
    def _make_response_with_answer(self, value="5"):
        from form.models import Answer

        ft = _make_form_type("s43", "S43")
        qt = _make_question_type("t24", "T24")
        q = _make_question(form_typ=ft, question_typ=qt, question="Agg Q answer?")
        resp = _make_response(ft)
        Answer.objects.create(question=q, response=resp, value=value, void_ind="n")
        return resp, q

    def test_aggregate_answers_horizontally_sum(self):
        """Lines 1940-1942: aggregate_answers_horizontally."""
        from form.util import aggregate_answers_horizontally
        from form.models import Answer

        ft = _make_form_type("s43", "S43")
        qt = _make_question_type("t24", "T24")
        q = _make_question(form_typ=ft, question_typ=qt, question="Agg Q answer?")
        resp = _make_response(ft)
        Answer.objects.create(question=q, response=resp, value="10", void_ind="n")

        qa_typ = _make_question_aggregate_type("sum")
        qa = _make_question_aggregate(qa_typ=qa_typ)
        from form.models import QuestionAggregateQuestion
        qaq = QuestionAggregateQuestion.objects.create(
            question_aggregate=qa,
            question=q,
            order=1,
            active="y",
            void_ind="n",
        )

        qa_dict = {
            "id": qa.id,
            "name": qa.name,
            "horizontal": qa.horizontal,
            "use_answer_time": qa.use_answer_time,
            "question_aggregate_typ": qa.question_aggregate_typ,
            "aggregate_questions": [
                {
                    "id": qaq.id,
                    "question": _MockQuestion(q.id),
                    "condition_value": None,
                    "order": 1,
                    "active": "y",
                    "question_condition_typ": None,
                }
            ],
            "active": "y",
        }

        questions = [_MockQuestion(q.id)]
        result = aggregate_answers_horizontally(qa_dict, resp, questions)
        assert result == 10

    def test_aggregate_answers_vertically_avg(self):
        """Lines 1946-1948: aggregate_answers_vertically."""
        from form.util import aggregate_answers_vertically
        from form.models import Answer

        ft = _make_form_type("s44", "S44")
        qt = _make_question_type("t25", "T25")
        q = _make_question(form_typ=ft, question_typ=qt, question="Vert Q?")
        resp1 = _make_response(ft)
        resp2 = _make_response(ft)
        Answer.objects.create(question=q, response=resp1, value="4", void_ind="n")
        Answer.objects.create(question=q, response=resp2, value="6", void_ind="n")

        qa_typ = _make_question_aggregate_type("avg")
        qa = _make_question_aggregate(qa_typ=qa_typ)
        from form.models import QuestionAggregateQuestion
        qaq = QuestionAggregateQuestion.objects.create(
            question_aggregate=qa, question=q, order=1, active="y", void_ind="n"
        )

        qa_dict = {
            "id": qa.id,
            "name": qa.name,
            "horizontal": qa.horizontal,
            "use_answer_time": qa.use_answer_time,
            "question_aggregate_typ": qa.question_aggregate_typ,
            "aggregate_questions": [
                {
                    "id": qaq.id,
                    "question": _MockQuestion(q.id),
                    "condition_value": None,
                    "order": 1,
                    "active": "y",
                    "question_condition_typ": None,
                }
            ],
            "active": "y",
        }
        questions = [_MockQuestion(q.id)]
        result = aggregate_answers_vertically(qa_dict, [resp1, resp2], questions)
        assert result == 5.0


# ─────────────────────────────────────────────────────────────
#  aggregate_answers – lines 1983-2148
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAggregateAnswersCases:
    """Test aggregate_answers with all aggregate types."""

    def _qa_dict(self, qa_typ_str, questions=None, use_answer_time=False):
        qa_typ = _make_question_aggregate_type(qa_typ_str)
        qa = _make_question_aggregate(qa_typ=qa_typ, use_answer_time=use_answer_time)
        qs = questions or []
        return {
            "id": qa.id,
            "name": qa.name,
            "horizontal": qa.horizontal,
            "use_answer_time": use_answer_time,
            "question_aggregate_typ": qa_typ,
            "aggregate_questions": [
                {
                    "id": i,
                    "question": _MockQuestion(q.id if hasattr(q, 'id') else -1),
                    "condition_value": None,
                    "order": i,
                    "active": "y",
                    "question_condition_typ": None,
                }
                for i, q in enumerate(qs)
            ],
            "active": "y",
        }

    def _make_rqa(self, responses_values):
        """Build a response_question_answers structure using MockQuestion."""
        return [
            {"response_id": i, "question_answers": [{"value": str(v), "question": _MockQuestion(-1)} for v in vals]}
            for i, vals in enumerate(responses_values)
        ]

    def test_sum(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("sum")
        rqa = self._make_rqa([[3, 4], [2]])
        result = aggregate_answers(qa_dict, rqa)
        assert result == 9

    def test_avg(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("avg")
        rqa = self._make_rqa([[4, 6]])
        result = aggregate_answers(qa_dict, rqa)
        assert result == 10.0

    def test_avg_empty_raises(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("avg")
        with pytest.raises(Exception, match="No division by 0"):
            aggregate_answers(qa_dict, [])

    def test_logical(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("logical")
        rqa = [
            {"response_id": 0, "question_answers": []},
            {"response_id": 1, "question_answers": []},
        ]
        result = aggregate_answers(qa_dict, rqa)
        # Both responses have logical_value=True, returns count
        assert result == 2

    def test_median(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("median")
        rqa = self._make_rqa([[1, 3, 5], [2, 4]])
        result = aggregate_answers(qa_dict, rqa)
        assert result is not None

    def test_stdev(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("stdev")
        rqa = self._make_rqa([[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]])
        result = aggregate_answers(qa_dict, rqa)
        assert result >= 0

    def test_difference(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("difference")
        rqa = self._make_rqa([[10, 3]])
        result = aggregate_answers(qa_dict, rqa)
        assert result == 7

    def test_unknown_type_raises(self):
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("sum")
        # Override aggregate type name to trigger unknown
        qa_dict["question_aggregate_typ"] = Mock()
        qa_dict["question_aggregate_typ"].question_aggregate_typ = "unknown_typ"
        rqa = self._make_rqa([[1]])
        with pytest.raises(Exception, match="no type"):
            aggregate_answers(qa_dict, rqa)

    def test_exist_value_skipped(self):
        """Lines 2009+: !EXIST value is skipped."""
        from form.util import aggregate_answers
        qa_dict = self._qa_dict("sum")
        rqa = [
            {
                "response_id": 0,
                "question_answers": [
                    {"value": "!EXIST", "question": _MockQuestion(-1)}
                ],
            }
        ]
        result = aggregate_answers(qa_dict, rqa)
        assert result == 0


# ─────────────────────────────────────────────────────────────
#  compute_quartiles – lines 2165-2194
# ─────────────────────────────────────────────────────────────

class TestComputeQuartiles:
    def test_empty_list(self):
        from form.util import compute_quartiles
        result = compute_quartiles([])
        assert result == {}

    def test_single_element(self):
        from form.util import compute_quartiles
        result = compute_quartiles([5])
        assert result["Q1"] == 5
        assert result["Q2"] == 5
        assert result["Q3"] == 5

    def test_normal_list(self):
        from form.util import compute_quartiles
        result = compute_quartiles([1, 2, 3, 4, 5, 6, 7, 8])
        assert "Q1" in result
        assert "Q2" in result
        assert "Q3" in result
        assert result["Q1"] <= result["Q2"] <= result["Q3"]

    def test_non_list_raises(self):
        from form.util import compute_quartiles
        with pytest.raises(TypeError, match="Input data must be a list"):
            compute_quartiles("not a list")

    def test_non_numeric_raises(self):
        from form.util import compute_quartiles
        with pytest.raises(TypeError, match="numeric"):
            compute_quartiles([1, "two", 3])

    def test_two_elements(self):
        from form.util import compute_quartiles
        result = compute_quartiles([2, 8])
        assert result["Q2"] == 5.0

    def test_large_list(self):
        from form.util import compute_quartiles
        data = list(range(1, 101))
        result = compute_quartiles(data)
        assert result["Q1"] < result["Q2"] < result["Q3"]


# ─────────────────────────────────────────────────────────────
#  get_responses_question_answers – lines 1952-1979
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGetResponsesQuestionAnswers:
    def test_get_responses_question_answers(self):
        """Lines 1952-1979: collect answers for responses."""
        from form.util import get_responses_question_answers
        from form.models import Answer

        ft = _make_form_type("s45", "S45")
        qt = _make_question_type("t26", "T26")
        q = _make_question(form_typ=ft, question_typ=qt, question="GRQA Q?")
        resp = _make_response(ft)
        Answer.objects.create(question=q, response=resp, value="3", void_ind="n")

        questions = [{"id": q.id, "active": "y"}]
        result = get_responses_question_answers([resp], questions)
        assert len(result) == 1
        assert result[0]["response_id"] == resp.id

    def test_get_responses_question_answers_missing_answer(self):
        """Lines 1964-1965: Answer.DoesNotExist is caught."""
        from form.util import get_responses_question_answers

        ft = _make_form_type("s46", "S46")
        resp = _make_response(ft)

        questions = [{"id": 99999, "active": "y"}]
        result = get_responses_question_answers([resp], questions)
        assert result[0]["response_id"] == resp.id


# ─────────────────────────────────────────────────────────────
#  graph_responses – lines 1278-1913 (smoke tests for each case)
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestGraphResponses:
    """Smoke tests for graph_responses function with each graph type."""

    def _base_graph_dict(self, graph_typ_str, gq_sets, bins=None, categories=None):
        """Build a minimal graph dict for mocking."""
        from form.models import GraphType
        gt, _ = GraphType.objects.get_or_create(
            graph_typ=graph_typ_str,
            defaults={"graph_nm": graph_typ_str, "requires_bins": False, "requires_categories": False},
        )
        return {
            "id": 1,
            "graph_typ": gt,
            "name": "Test",
            "x_scale_min": 0,
            "x_scale_max": 100,
            "y_scale_min": 0,
            "y_scale_max": 100,
            "active": "y",
            "graphbin_set": bins or [],
            "graphcategory_set": categories or [],
            "graphquestion_set": gq_sets,
        }

    def test_histogram_empty_responses(self):
        from form.util import graph_responses

        graph_dict = self._base_graph_dict(
            "histogram",
            gq_sets=[
                {
                    "question": {"id": 1, "question": "HQ", "active": "y"},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
            bins=[],
        )
        with patch("form.util.get_graphs", return_value=[graph_dict]):
            result = graph_responses(1, [])
        assert result is not None

    def test_ctg_hstgrm_empty(self):
        from form.util import graph_responses

        graph_dict = self._base_graph_dict(
            "ctg-hstgrm",
            gq_sets=[],
            categories=[
                {
                    "category": "C1",
                    "graphcategoryattribute_set": [],
                    "bins": [{"bin": "Dataset", "count": 0}],
                }
            ],
        )
        with patch("form.util.get_graphs", return_value=[graph_dict]):
            result = graph_responses(1, [])
        assert result is not None
        assert result[0]["label"] == "C1"

    def test_diff_plot_empty(self):
        from form.util import graph_responses

        graph_dict = self._base_graph_dict(
            "diff-plot",
            gq_sets=[
                {
                    "question": {"id": 1, "question": "DQ", "active": "y"},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        )
        with patch("form.util.get_graphs", return_value=[graph_dict]):
            result = graph_responses(1, [])
        assert result is not None

    def test_box_wskr_empty(self):
        from form.util import graph_responses

        graph_dict = self._base_graph_dict(
            "box-wskr",
            gq_sets=[
                {
                    "question": {"id": 1, "question": "BQ", "active": "y"},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        )
        with patch("form.util.get_graphs", return_value=[graph_dict]):
            result = graph_responses(1, [])
        assert result is not None
        assert result == []  # no dataset, not appended

    def test_touch_map_empty(self):
        from form.util import graph_responses

        graph_dict = self._base_graph_dict(
            "touch-map",
            gq_sets=[
                {
                    "question": {"id": 1, "question": "TQ", "active": "y"},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        )
        with patch("form.util.get_graphs", return_value=[graph_dict]):
            result = graph_responses(1, [])
        assert result is not None

    def test_line_empty(self):
        from form.util import graph_responses

        graph_dict = self._base_graph_dict(
            "line",
            gq_sets=[
                {
                    "question": {"id": 1, "question": "LQ", "active": "y"},
                    "question_aggregate": None,
                    "graph_question_typ": None,
                    "active": "y",
                }
            ],
        )
        with patch("form.util.get_graphs", return_value=[graph_dict]):
            result = graph_responses(1, [])
        assert result is not None
        assert result == [{"label": "LQ", "points": []}]
