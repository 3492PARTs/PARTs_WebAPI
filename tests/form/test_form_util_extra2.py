"""
Extra coverage tests for form/util.py.
Targets:
  line 303 (save_question: question_flow_id_set)
  line 309 (save_question: update existing scout question)
  lines 457, 466 (save_response/get_response)
  lines 485-497 (get_responses)
  lines 601 (save_question_aggregate: update existing qaq)
  lines 975-976 (save_flow: update existing FlowQuestion)
  lines 994-997 (save_flow: pit/field scout question flow creation)
  lines 2129-2152 (aggregate_answers: difference branch)
  lines 2192 (aggregate_answers: stdev branch)
  lines 2206-2224 (send_email_notification)
"""
import pytest
from unittest.mock import patch, MagicMock
import datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_form_type(form_typ="contact", form_nm="Contact"):
    from form.models import FormType
    ft, _ = FormType.objects.get_or_create(
        form_typ=form_typ, defaults={"form_nm": form_nm}
    )
    return ft


def _create_question_type(qt="text"):
    from form.models import QuestionType
    qtyp, _ = QuestionType.objects.get_or_create(
        question_typ=qt, defaults={"question_typ_nm": qt.capitalize(), "void_ind": "n"}
    )
    return qtyp


def _create_question(form_typ_obj, qtyp, question_text="Q", order=1):
    from form.models import Question
    q = Question(
        question=question_text,
        form_typ=form_typ_obj,
        question_typ=qtyp,
        order=order,
        table_col_width="",
        required="n",
        active="y",
        void_ind="n",
    )
    q.save()
    return q


def _create_agg_type(typ="sum"):
    from form.models import QuestionAggregateType
    at, _ = QuestionAggregateType.objects.get_or_create(
        question_aggregate_typ=typ, defaults={"question_aggregate_nm": typ}
    )
    return at


# ---------------------------------------------------------------------------
# lines 302-303: save_question adds flow via question_flow_id_set
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveQuestionFlowIdSet:
    def test_save_question_flow_id_set(self):
        from form.util import save_question
        from form.models import FormType, FormSubType, Flow

        ft = _create_form_type("contact_q303", "Contact303")
        qtyp = _create_question_type("text")

        flow_typ = ft  # reuse
        flow = Flow(
            name="Flow Q303",
            single_run=False,
            form_based=False,
            form_typ=ft,
            void_ind="n",
        )
        flow.save()

        data = {
            "question": "TestQ303",
            "form_typ": {"form_typ": "contact_q303"},
            "question_typ": {"question_typ": "text"},
            "order": 1,
            "required": "n",
            "active": "y",
            "void_ind": "n",
            "table_col_width": "",
            "question_flow_id_set": [flow.id],
        }
        q = save_question(data)
        assert q is not None
        assert flow in q.question_flow.all()


# ---------------------------------------------------------------------------
# line 309: save_question with existing scout question id (pit form)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveQuestionUpdateScoutQuestion:
    def test_save_question_update_existing_scout_question(self):
        from form.util import save_question
        from form.models import FormType
        import scouting.models as sm

        # Need a pit FormType
        ft, _ = FormType.objects.get_or_create(
            form_typ="pit",
            defaults={"form_nm": "Pit"},
        )
        qtyp = _create_question_type("text")
        season = sm.Season.objects.create(
            season="2099sq309", current="y", game="G", manual="M"
        )
        form_q = _create_question(ft, qtyp, "BaseQ309", 5)
        sq = sm.Question(question=form_q, season=season, void_ind="n")
        sq.save()

        data = {
            "question": "UpdatedQ309",
            "form_typ": {"form_typ": "pit"},
            "question_typ": {"question_typ": "text"},
            "order": 5,
            "required": "n",
            "active": "y",
            "void_ind": "n",
            "table_col_width": "",
            "question_flow_id_set": [],
            "scout_question": {"id": sq.id},
        }

        with patch("scouting.util.get_current_season", return_value=season):
            result = save_question(data)

        assert result is not None


# ---------------------------------------------------------------------------
# line 466: save_response update existing Response
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveResponseUpdate:
    def test_save_response_update(self):
        from form.util import save_response
        from form.models import Response

        ft = _create_form_type("contact_sr466", "ContactSR466")
        resp = Response(form_typ=ft, archive_ind="n", void_ind="n")
        resp.save()

        data = {
            "response_id": resp.id,
            "form_typ": "contact_sr466",
            "time": datetime.datetime.now(tz=datetime.timezone.utc),
            "archive_ind": "y",
        }
        save_response(data)
        resp.refresh_from_db()
        assert resp.archive_ind == "y"


# ---------------------------------------------------------------------------
# line 457: get_response returns questions with answers
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetResponse:
    def test_get_response(self):
        from form.util import get_response
        from form.models import Response

        ft = _create_form_type("contact_gr457", "ContactGR457")
        resp = Response(form_typ=ft, archive_ind="n", void_ind="n")
        resp.save()

        result = get_response(resp.id)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# lines 485-497: get_responses
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestGetResponses:
    def test_get_responses_empty(self):
        from form.util import get_responses

        _create_form_type("contact_gr485", "ContactGR485")
        result = get_responses("contact_gr485", "n")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# line 601: save_question_aggregate with update existing qaq
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveQuestionAggregateUpdateQAQ:
    def test_update_existing_qaq(self):
        from form.util import save_question_aggregate
        from form.models import QuestionAggregate, QuestionAggregateQuestion

        agg_typ = _create_agg_type("sum")
        ft = _create_form_type("contact_qa601", "ContactQA601")
        qtyp = _create_question_type("text")
        q = _create_question(ft, qtyp, "QA601", 1)

        qa = QuestionAggregate(
            name="QA601",
            horizontal=False,
            use_answer_time=False,
            active="y",
            question_aggregate_typ=agg_typ,
            void_ind="n",
        )
        qa.save()
        qaq = QuestionAggregateQuestion(
            question_aggregate=qa,
            question=q,
            order=1,
            active="y",
            void_ind="n",
        )
        qaq.save()

        data = {
            "id": qa.id,
            "name": "QA601 Updated",
            "horizontal": False,
            "use_answer_time": False,
            "active": "y",
            "question_aggregate_typ": {"question_aggregate_typ": "sum"},
            "aggregate_questions": [
                {
                    "id": qaq.id,
                    "question": {"id": q.id},
                    "question_condition_typ": None,
                    "condition_value": None,
                    "order": 1,
                    "active": "y",
                }
            ],
        }
        result = save_question_aggregate(data)
        assert result.name == "QA601 Updated"


# ---------------------------------------------------------------------------
# lines 975-976: save_flow update existing FlowQuestion
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveFlowUpdateFlowQuestion:
    def test_save_flow_update_existing_flow_question(self):
        from form.util import save_flow
        from form.models import Flow, FlowQuestion, FormType

        ft = _create_form_type("contact_sf976", "ContactSF976")
        qtyp = _create_question_type("text")
        q = _create_question(ft, qtyp, "FlowQ976", 1)
        flow = Flow(name="SF976 Flow", single_run=False, form_based=False, form_typ=ft, void_ind="n")
        flow.save()
        fq = FlowQuestion(flow=flow, question=q, press_to_continue=False, order=1, void_ind="n")
        fq.save()

        data = {
            "id": flow.id,
            "name": "SF976 Flow Updated",
            "single_run": False,
            "form_based": False,
            "form_typ": {"form_typ": "contact_sf976"},
            "void_ind": "n",
            "flow_questions": [
                {
                    "id": fq.id,
                    "question": {
                        "id": q.id,
                        "question": "FlowQ976",
                        "form_typ": {"form_typ": "contact_sf976"},
                        "question_typ": {"question_typ": "text"},
                        "order": 1,
                        "required": "n",
                        "active": "y",
                        "void_ind": "n",
                        "table_col_width": "",
                        "question_flow_id_set": [],
                    },
                    "press_to_continue": False,
                    "order": 2,
                }
            ],
        }
        result = save_flow(data)
        assert result.name == "SF976 Flow Updated"


# ---------------------------------------------------------------------------
# lines 994-997: save_flow for pit/field creates scout QuestionFlow
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSaveFlowPitCreatesQuestionFlow:
    def test_save_flow_pit_creates_scout_question_flow(self):
        from form.util import save_flow
        from form.models import FormType, Flow
        import scouting.models as sm

        ft, _ = FormType.objects.get_or_create(
            form_typ="pit", defaults={"form_nm": "Pit"}
        )
        season = sm.Season.objects.create(season="2099sf997", current="y", game="G", manual="M")

        data = {
            "name": "SF997 Pit Flow",
            "single_run": False,
            "form_based": False,
            "form_typ": {"form_typ": "pit"},
            "void_ind": "n",
            "flow_questions": [],
        }

        with patch("scouting.util.get_current_season", return_value=season):
            result = save_flow(data)

        assert result is not None
        assert sm.QuestionFlow.objects.filter(flow=result, season=season).exists()


# ---------------------------------------------------------------------------
# lines 2206-2224: send_email_notification
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestSendEmailNotification:
    def test_send_email_notification_no_emails(self):
        from form.util import send_email_notification
        from form.models import Response

        ft = _create_form_type("contact_sen2206", "ContactSEN")
        resp = Response(form_typ=ft, archive_ind="n", void_ind="n")
        resp.save()

        # Should not raise even if no email answers
        send_email_notification(resp)

    def test_send_email_notification_with_email_answer(self):
        from form.util import send_email_notification
        from form.models import Response, Answer

        ft = _create_form_type("contact_sen2206b", "ContactSENb")
        qtyp = _create_question_type("text")

        from form.models import Question as FQ
        q = FQ(
            question="School Email",
            form_typ=ft,
            question_typ=qtyp,
            order=1,
            required="n",
            active="y",
            void_ind="n",
        )
        q.save()

        resp = Response(form_typ=ft, archive_ind="n", void_ind="n")
        resp.save()

        ans = Answer(response=resp, question=q, value="test@example.com", void_ind="n")
        ans.save()

        with patch("form.util.send_email") as mock_send:
            send_email_notification(resp)

        mock_send.assert_called_once()
