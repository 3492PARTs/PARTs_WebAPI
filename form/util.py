from django.conf import settings
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import Lower

import alerts.util
import form.models
import scouting.models
import scouting.util
import user.util
from form.models import (
    FormType,
    Question,
    Response,
    Answer,
    QuestionOption,
    FormSubType,
    QuestionType,
    QuestionAggregate,
    QuestionAggregateType,
    QuestionCondition, Flow, FlowAnswer,
    QuestionConditionType, FlowCondition, QuestionFlow
)
from scouting.models import Match, Season, FieldResponse, PitResponse, Event


def get_questions(form_typ: str = None, active: str = "", form_sub_typ: str = "", not_in_flow = False, is_conditional=False, is_not_conditional=False, qid = None):
    questions = []
    q_season = Q()
    q_active_ind = Q()
    q_form_sub_typ_q = Q()
    q_not_in_flow = Q()
    q_is_conditional = Q()
    q_is_not_conditional = Q()
    q_id = Q()
    q_form_typ = Q()

    if form_typ is not None:
        q_form_typ = Q(form_typ_id=form_typ)

    if form_typ == "field" or form_typ == "pit":
        current_season = scouting.util.get_current_season()
        scout_questions = scouting.models.Question.objects.filter(
            Q(void_ind="n") & Q(season=current_season)
        )
        q_season = Q(id__in=set(sq.question.id for sq in scout_questions))

    if active != "":
        q_active_ind = Q(active=active)

    if form_sub_typ is None:
        q_form_sub_typ_q = Q(form_sub_typ_id__isnull=True)
    elif form_sub_typ != "":
        q_form_sub_typ_q = Q(form_sub_typ_id=form_sub_typ)

    if not_in_flow:
        q_not_in_flow = Q(in_flow=False)

    if is_conditional:
        q_is_conditional = Q(Q(condition_question_to__void_ind="n") & Q(condition_question_to__active="y"))

    if is_not_conditional:
        q_is_not_conditional = Q(Q(condition_question_to__isnull=True) | (Q(condition_question_to__isnull=False) & (Q(condition_question_to__active="n") | Q(condition_question_to__void_ind="y"))))

    if qid is not None:
        q_id = Q(id=qid)

    qs = (
        Question.objects
        .prefetch_related("questionoption_set", "scout_question", "question_typ", "condition_question_from", "condition_question_to", "questionflow_set", "question_typ__scout_question_type")
        .annotate(
            in_flow=Exists(
                QuestionFlow.objects.filter(Q(question_id=OuterRef("pk")) & Q(active="y") & Q(void_ind="n"))
            )
        ).filter(
            q_id
            & q_season
            & q_form_typ
            & q_form_sub_typ_q
            & q_active_ind
            & q_not_in_flow
            & q_is_conditional
            & q_is_not_conditional
            & Q(void_ind="n")
        )
        .order_by("form_sub_typ__order", "order")
    )

    for q in qs:
        questions.append(format_question_values(q))

    return questions


def format_question_values(in_question: Question):
    # Scout question type
    try:
        sqt = in_question.question_typ.scout_question_type.get(void_ind="n")
        scout_question_type = {
            "id": sqt.id,
            "scorable": sqt.scorable
        }
    except scouting.models.QuestionType.DoesNotExist:
        scout_question_type = None

    # Question Type
    question_type = {
        "question_typ": in_question.question_typ.question_typ,
        "question_typ_nm": in_question.question_typ.question_typ_nm,
        "is_list": in_question.question_typ.is_list,
        "scout_question_type": scout_question_type
    }

    # Scout Question
    try:
        sq = in_question.scout_question.get(Q(void_ind="n"))

        scout_question = {
            "id": sq.id,
            "question_id": sq.id,
            "season_id": sq.season.id,
            "x": sq.x,
            "y": sq.y,
            "width": sq.width,
            "height": sq.height,
            "icon": sq.icon,
            "icon_only": sq.icon_only,
            "value_multiplier": sq.value_multiplier,
        }
        season = sq.season.id
    except scouting.models.Question.DoesNotExist as e:
        scout_question = None
        season = None

    # List of options if applicable
    questionoption_set = []
    for qo in in_question.questionoption_set.filter(Q(void_ind="n") & Q(active="y")):
        questionoption_set.append(
            {
                "question_opt_id": qo.question_opt_id,
                "question_id": qo.question_id,
                "option": qo.option,
                "active": qo.active,
            }
        )

    # Flag if question has conditions
    try:
        conditional_questions = in_question.condition_question_from.filter(
            Q(void_ind="n") & Q(active="y") & Q(question_to__active="y"))
    except QuestionCondition.DoesNotExist:
        conditional_questions = None

    # Flag if question is condition of another
    try:
        conditional_on_question = in_question.condition_question_to.get(Q(void_ind="n") & Q(active="y"))
    except QuestionCondition.DoesNotExist:
        conditional_on_question = None

    question_flows = in_question.questionflow_set.filter(Q(active="y") & Q(void_ind="n"))

    return {
        "id": in_question.id,
        "flow_id_set": set(qf.flow.id for qf in question_flows),
        "season_id": season,
        "question": in_question.question,
        "table_col_width": in_question.table_col_width,
        "order": in_question.order,
        "required": in_question.required,
        "active": in_question.active,
        "question_typ": question_type,
        "form_typ": in_question.form_typ,
        "form_sub_typ": in_question.form_sub_typ,
        "questionoption_set": questionoption_set,
        "display_value": f"{'' if in_question.active == 'y' else 'Deactivated: '} Order: {in_question.order}: {in_question.form_sub_typ.form_sub_nm + ': ' if in_question.form_sub_typ is not None else ''}{in_question.question}",
        "scout_question": scout_question,
        "question_conditional_on": conditional_on_question.question_from.id if conditional_on_question is not None else None,
        "question_condition_value": conditional_on_question.value if conditional_on_question is not None else None,
        "question_condition_typ": conditional_on_question.question_condition_typ if conditional_on_question is not None else None,
        "conditional_question_id_set": set(cq.question_to.id for cq in conditional_questions),
    }


def save_question(question):
    current_season = None
    if question["form_typ"]["form_typ"] in ["pit", "field"]:
        current_season = scouting.util.get_current_season()

    required = question.get("required", "n")
    required = required if required != "" else "n"

    if question.get("question_id", None) is not None:
        q = Question.objects.get(question_id=question["question_id"])
        q.question = question["question"]
        q.table_col_width = question["table_col_width"]
        q.question_typ_id = question["question_typ"]["question_typ"]
        q.order = question["order"]
        q.required = required
        q.active = question["active"]
    else:
        q = Question(
            question_typ_id=question["question_typ"]["question_typ"],
            form_typ_id=question["form_typ"]["form_typ"],
            question=question["question"],
            table_col_width=question["table_col_width"],
            order=question["order"],
            active=question["active"],
            required=required,
            void_ind="n",
        )

    q.form_sub_typ_id = None if question.get("form_sub_typ", None) is None else question["form_sub_typ"].get("form_sub_typ", None)

    for qfid in question.get("question_flow_id_set", []):
        q.question_flow.add(Flow.objects.get(id=qfid))

    q.save()

    if question["form_typ"]["form_typ"] in ["pit", "field"]:
        if question.get("scout_question", None).get("id", None) is not None:
            sq = scouting.models.Question.objects.get(id=question["scout_question"]["id"])
        else:
            sq = scouting.models.Question(question=q)

        if sq.season is None:
            sq.season = current_season

        scout_question = question.get("scout_question", None)
        sq.x = scout_question.get("x", None)
        sq.y = scout_question.get("y", None)
        sq.width = scout_question.get("width", None)
        sq.height = scout_question.get("height", None)
        sq.icon = scout_question.get("icon", None)
        sq.icon_only = scout_question.get("icon_only", False)
        sq.value_multiplier = scout_question.get("value_multiplier", False)
        sq.save()

    if question.get("id", None) is None:
        # If adding a new question we need to make a null answer for it for all questions already answered
        match question["form_typ"]["form_typ"]:
            case "pit":
                pit_responses = PitResponse.objects.filter(
                    Q(void_ind="n")
                    & Q(
                        event__in=Event.objects.filter(
                            Q(void_ind="n") & Q(season=current_season)
                        )
                    )
                )
                questions_answered = Response.objects.filter(
                    Q(void_ind="n")
                    & Q(response_id__in=set(pr.response_id for pr in pit_responses))
                )
            case "field":
                field_responses = FieldResponse.objects.filter(
                    Q(void_ind="n")
                    & Q(
                        event__in=Event.objects.filter(
                            Q(void_ind="n") & Q(season=current_season)
                        )
                    )
                )
                questions_answered = Response.objects.filter(
                    Q(void_ind="n")
                    & Q(response_id__in=set(fr.response_id for fr in field_responses))
                )
            case _:
                questions_answered = Response.objects.filter(
                    Q(void_ind="n") & Q(form_typ_id=question["form_typ"])
                )

        for qa in questions_answered:
            Answer(
                response=qa, question=q, value="!EXIST", void_ind="n"
            ).save()

    if (
            question["question_typ"]["is_list"] == "y"
            and len(question.get("questionoption_set", [])) <= 0
    ):
        raise Exception("Select questions must have options.")

    for op in question.get("questionoption_set", []):
        if op.get("question_opt_id", None) is not None:
            qop = QuestionOption.objects.get(question_opt_id=op["question_opt_id"])
            qop.option = op["option"]
            qop.active = op["active"]
        else:
            qop = QuestionOption(
                option=op["option"], question=q, active=op["active"], void_ind="n"
            )

        qop.save()


def get_question_types():
    qts = QuestionType.objects.filter(void_ind="n").order_by(
        Lower("question_typ_nm")
    )
    question_types = []

    for qt in qts:
        try:
            sqt = qt.scout_question_type.get(void_ind="n")
            scout_question_type = {
                "id": sqt.id,
                "scorable": sqt.scorable
            }
        except scouting.models.QuestionType.DoesNotExist:
            scout_question_type = None

        question_types.append({
            "question_typ": qt.question_typ,
            "question_typ_nm": qt.question_typ_nm,
            "is_list": qt.is_list,
            "scout_question_type": scout_question_type
        })

    return question_types


def get_form_sub_types(form_typ: str):
    sub_types = FormSubType.objects.filter(form_typ=form_typ).order_by(
        "order", Lower("form_sub_nm")
    )
    return sub_types


def save_or_update_answer(data, response: Response):
    q_question = Q()
    if data.get("question", None) is not None:
        q_question = Q(question_id=data["question"]["id"])

    q_question_flow = Q()
    if data.get("flow", None) is not None:
        q_question_flow = Q(flow_id=data["flow"]["id"])

    # Get answer to update or save new
    try:
        answer = Answer.objects.get(
            Q(response=response)
            & q_question
            & q_question_flow
            & Q(void_ind="n")
        )
        answer.value = data.get("value", "")
        answer.save()
    except Answer.DoesNotExist:
        answer = Answer(
            question_id=data.get("question", {}).get("id", None), flow_id=data.get("flow", {}).get("id", None), value=data.get("value", ""), response=response, void_ind="n"
        )
        answer.save()


    for flow_answer in data.get("flow_answers", []):
        save_question_flow_answer(flow_answer, answer)

    return answer


def save_question_flow_answer(data, answer: Answer):
    flow_answer = FlowAnswer(answer=answer,
                     question_id=data['question']['id'], value=data.get("value", ""), value_time=data['value_time'], void_ind="n"
                     )
    flow_answer.save()
    return flow_answer


def get_response(response_id: int):
    res = Response.objects.get(Q(response_id=response_id) & Q(void_ind="n"))
    questions = get_questions(res.form_typ, "y")

    for question in questions:
        question["answer"] = get_response_question_answer(res, question["id"])

    return questions


def save_response(data):
    if data.get("response_id", None) is None:
        response = Response()
    else:
        response = Response.objects.get(response_id=data["response_id"])

    response.form_typ_id = data["form_typ"]
    response.time = data["time"]
    response.archive_ind = data["archive_ind"]

    response.save()


def delete_response(response_id: int):
    res = Response.objects.get(response_id=response_id)

    res.void_ind = "y"
    res._change_reason = "User deleted"
    res.save()

    return res


def get_responses(form_typ: int, archive_ind: str):
    responses = []
    resps = Response.objects.filter(
        Q(form_typ__form_typ=form_typ) & Q(archive_ind=archive_ind) & Q(void_ind="n")
    ).order_by("-time")

    for res in resps:
        questions = get_questions(res.form_typ, "y")

        for question in questions:
            question["answer"] = get_response_question_answer(
                res, question["id"]
            )

        responses.append(
            {
                "response_id": res.response_id,
                "form_typ": res.form_typ.form_typ,
                "time": res.time,
                "archive_ind": res.archive_ind,
                "questionanswer_set": questions,
            }
        )

    return responses


def get_response_question_answer(response: form.models.Response, question_id: int):
    try:
        answer = Answer.objects.get(
            Q(question_id=question_id) & Q(response=response) & Q(void_ind="n")
        ).value
    except Answer.DoesNotExist:
        answer = "!FOUND"

    return answer


def get_question_aggregates(form_typ: str):
    question_aggregates = []
    season = Q()

    if form_typ == "field" or form_typ == "pit":
        current_season = scouting.util.get_current_season()
        scout_questions = scouting.models.Question.objects.filter(
            Q(void_ind="n") & Q(season=current_season)
        )
        season = Q(
            questions__question_id__in=set(sq.id for sq in scout_questions)
        )

    qas = QuestionAggregate.objects.filter(
        Q(void_ind="n") & Q(questions__form_typ=form_typ) & season
    ).distinct()
    for qa in qas:
        question_aggregates.append(
            {
                "question_aggregate_id": qa.question_aggregate_id,
                "field_name": qa.field_name,
                "question_aggregate_typ": qa.question_aggregate_typ,
                "questions": list(
                    format_question_values(q)
                    for q in qa.questions.filter(Q(void_ind="n"))
                ),
                "active": qa.active,
            }
        )

    return question_aggregates


def get_question_aggregate_types():
    return QuestionAggregateType.objects.filter(Q(void_ind="n"))


def save_question_aggregate(data):
    if data.get("question_aggregate_id", None) is not None:
        qa = QuestionAggregate.objects.get(
            Q(question_aggregate_id=data["question_aggregate_id"])
        )
    else:
        qa = QuestionAggregate()

    qa.field_name = data["field_name"]
    qa.active = data["active"]
    qa.question_aggregate_typ = QuestionAggregateType.objects.get(
        Q(void_ind="n")
        & Q(
            question_aggregate_typ=data["question_aggregate_typ"][
                "question_aggregate_typ"
            ]
        )
    )
    qa.save()

    questions = Question.objects.filter(
        question_id__in=set(q["question_id"] for q in data["questions"])
    )

    for q in questions:
        qa.questions.add(q)

    qa.save()

    remove = qa.questions.all().filter(
        ~Q(question_id__in=set(q.id for q in questions))
    )
    for r in remove:
        qa.questions.remove(r)

    qa.save()

    return qa


def get_question_condition(form_typ: str):
    parsed_question_conditions = []
    season = Q()

    if form_typ == "field" or form_typ == "pit":
        current_season = scouting.util.get_current_season()
        scout_questions = scouting.models.Question.objects.filter(
            Q(void_ind="n") & Q(season=current_season)
        )
        season = Q(
            question_from__in=[q.question for q in scout_questions]
        )

    question_conditions = QuestionCondition.objects.filter(
        Q(void_ind="n") & Q(question_from__form_typ=form_typ) & season
    )

    for qc in question_conditions:
        parsed_question_conditions.append(
            {
                "question_condition_id": qc.question_condition_id,
                "question_condition_typ": qc.question_condition_typ,
                "value": qc.value,
                "question_from": format_question_values(qc.question_from),
                "question_to": format_question_values(qc.question_to),
                "active": qc.active,
            }
        )

    return parsed_question_conditions


def get_question_condition_types():
    return QuestionConditionType.objects.filter(void_ind="n")


def save_question_condition(data):
    if data.get("question_condition_id", None) is not None:
        qc = QuestionCondition.objects.get(
            question_condition_id=data["question_condition_id"]
        )
    else:
        qc = QuestionCondition()

    qc.value = data["value"]
    qc.question_condition_typ_id = data["question_condition_typ"]["question_condition_typ"]
    qc.active = data["active"]

    qc.question_from = Question.objects.get(
        question_id=data["question_from"]["question_id"]
    )
    qc.question_to = Question.objects.get(
        question_id=data["question_to"]["question_id"]
    )

    qc.save()

    return qc


def format_question_condition_values(qc: QuestionCondition):
    return {
        "question_condition_id": qc.question_condition_id,
        "condition": qc.condition,
        "question_from": format_question_values(qc.question_from),
        "question_to": format_question_values(qc.question_to),
        "active": qc.active,
    }


def get_flow_condition(form_typ: str):
    parsed = []

    q_season = Q()

    if form_typ == "field" or form_typ == "pit":
        current_season = scouting.util.get_current_season()
        q_season = Q(flow_from__scout_question_flow__season=current_season)

    flow_conditions = FlowCondition.objects.filter(
        Q(void_ind="n") & Q(flow_from__form_typ=form_typ) & q_season
    )

    for qc in flow_conditions:
        parsed.append(
            {
                "id": qc.id,
                "flow_from": format_flow_values(qc.flow_from),
                "flow_to": format_flow_values(qc.flow_to),
                "active": qc.active,
            }
        )

    return parsed


def save_question_flow_condition(data):
    if data.get("id", None) is not None:
        qfc = FlowCondition.objects.get(
            id=data["id"]
        )
    else:
        qfc = FlowCondition()

    qfc.active = data["active"]

    qfc.flow_from_id = data["flow_from"]["id"]
    qfc.flow_to_id = data["flow_to"]["id"]

    qfc.save()

    return qfc


def format_flow_values(flow: Flow):
    # Flag if question flow has conditions
    try:
        count = flow.condition_flow_from.filter(
            Q(void_ind="n") & Q(flow_to__void_ind="n")).count()
        has_conditions = "y" if count > 0 else "n"
    except FlowCondition.DoesNotExist:
        has_conditions = "n"

    # Flag if question is condition of another
    try:
        question_flow_conditional_on = flow.condition_flow_to.get(Q(void_ind="n"))
    except FlowCondition.DoesNotExist:
        question_flow_conditional_on = None

    return {
            "id": flow.id,
            "name": flow.name,
            "single_run": flow.single_run,
            "form_typ": flow.form_typ,
            "form_sub_typ": flow.form_sub_typ if flow.form_sub_typ is not None else None,
            "question_flows": [{
                "id": qf.id,
                "flow_id": flow.id,
                "question": format_question_values(qf.question),
                "order": qf.order,
                "active": qf.active
            } for qf in QuestionFlow.objects.filter(Q(flow=flow) & Q(active="y") & Q(void_ind="n")).order_by("question__order")],
            "void_ind": flow.void_ind,
            "has_conditions": has_conditions,
            "flow_conditional_on": question_flow_conditional_on.flow_from.id if question_flow_conditional_on is not None else None
        }



def get_form_questions(
        form_typ: str
):
    form_type = FormType.objects.get(form_typ=form_typ)
    form_parsed = {
        "form_type": form_type,
        "form_sub_types": []
    }

    sub_types = FormSubType.objects.filter(form_typ=form_type)
    for st in sub_types:
        qs = get_questions("field", "y", st.form_sub_typ, not_in_flow=True)
        qfs = get_flows(form_typ="field", form_sub_typ=st.form_sub_typ)

        form_parsed["form_sub_types"].append({
            "form_sub_typ": st,
            "questions": qs,
            "question_flows": qfs
        })

    #print(form_parsed)

    return form_parsed


def get_response_answers(response: Response):
    answers = []

    question_answers = Answer.objects.filter(Q(response=response) & Q(void_ind="n"))

    for question_answer in question_answers:
        answers.append({
            "question": get_questions(qid=question_answer.question.id)[0] if question_answer.question is not None else None,
            "flow": get_flows(question_answer.flow.id)[0] if question_answer.flow is not None else None,
            "answer": question_answer.value,
            "flow_answers": list({
                "question": format_question_values(qfa.question),
                "value": qfa.value,
                "value_time": qfa.value_time
                                         } for qfa in question_answer.flowanswer_set.filter(void_ind="n").order_by("value_time"))
        })

    return answers


def save_field_response(data, user_id):
    current_event = scouting.util.get_current_event()
    # Build field scout object and check for match
    try:
        m = Match.objects.get(match_key=data.get("match_key", None))
    except Match.DoesNotExist:
        m = None

    form_type = FormType.objects.get(form_typ=data["form_typ"])

    response = form.models.Response(form_typ=form_type)
    response.save()

    field_response = FieldResponse(
        event=current_event,
        team_id=data["team_id"],
        match=m,
        user_id=user_id,
        response=response,
        void_ind="n",
    )
    field_response.save()

    # Save the answers against the response object
    for answer in data.get("answers", []):
        save_or_update_answer(answer, response)

    # Check if previous match is missing any results
    """
    if (
        m is not None
        and m.match_number > 1
        and len(m.scoutfield_set.filter(void_ind="n")) == 1
    ):
        prev_m = Match.objects.get(
            Q(void_ind="n")
            & Q(event=m.event)
            & Q(comp_level=m.comp_level)
            & Q(match_number=m.match_number - 1)
        )

        sfs = prev_m.scoutfield_set.filter(void_ind="n")

        if len(set(sf.team_no for sf in sfs)) < 6:
            users = ""
            for sf in sfs:
                users += sf.user.get_full_name() + ", "
            users = users[0 : len(users) - 2]
            alert = alerts.util.stage_scout_admin_alerts(
                f"Match: {prev_m.match_number} is missing a result.",
                f"We have results from: {users}",
            )

            for a in alert:
                for acct in ["txt", "notification"]:
                    alerts.util.stage_alert_channel_send(
                        a, acct
                    )

    # Check if user is under review and notify lead scouts
    try:
        user_info = request.user.scouting_user_info.get(
            void_ind="n"
        )
    except UserInfo.DoesNotExist:
        user_info = {}

    if user_info and user_info.under_review:
        alert = alerts.util.stage_scout_admin_alerts(
            f"Scout under review, {request.user.get_full_name()}, logged a new response.",
            f'Team: {sf.team_no.team_no} Match: {sf.match.match_number if sf.match else "No match"}\n@{sf.time.astimezone(pytz.timezone(sf.event.timezone)).strftime("%m/%d/%Y, %I:%M%p")}',
        )

        for a in alert:
            for acct in ["txt", "notification"]:
                alerts.util.stage_alert_channel_send(
                    a, acct
                )
    """
    return field_response


def save_pit_response(data, user_id):
    current_event = scouting.util.get_current_event()

    form_type = FormType.objects.get(form_typ=data["form_typ"])
    # Build or get pit scout object
    try:
        sp = PitResponse.objects.get(
            Q(team_id=data["team_id"]) & Q(void_ind="n") & Q(event=current_event)
        )
        response = sp.response

        if response.void_ind == "y":
            response = form.models.Response(form_typ=form_type)
            response.save()
            sp.response = response
            sp.save()
    except PitResponse.DoesNotExist:
        response = form.models.Response(form_typ=form_type)
        response.save()

        sp = PitResponse(
            event=current_event,
            team_id=data["team_id"],
            user_id=user_id,
            response=response,
            void_ind="n",
        )
        sp.save()

    # Save the answers against the response object
    for d in data.get("answers", []):
        save_or_update_answer(d, response)

    return sp


def save_answers(data):
    form_type = FormType.objects.get(form_typ=data["form_typ"])

    with transaction.atomic():
        response = form.models.Response(form_typ=form_type)
        response.save()

        # Save the answers against the response object
        for d in data.get("question_answers", []):
            save_or_update_answer(d, response)

    alert = []
    users = user.util.get_users_with_permission("site_forms_notif")
    for u in users:
        alert.append(
            alerts.util.stage_alert(
                u,
                form_type.form_nm,
                f'<a href="{settings.FRONTEND_ADDRESS}{"contact" if form_type.form_typ == "team-cntct" else "join/team-application"}?response_id={response.response_id}">A new response has been logged.</a>',
            )
        )
    for a in alert:
        for acct in ["email", "notification"]:
            alerts.util.stage_channel_send_for_all_channels(a, acct)


def get_flows(fid = None, form_typ=None, form_sub_typ=None):
    q_id = Q()
    if fid is not None:
        q_id = Q(id=fid)

    q_form_typ = Q()
    if form_typ is not None:
        q_form_typ = Q(form_typ_id=form_typ)

    q_form_sub_typ = Q()
    if form_sub_typ is not None:
        q_form_sub_typ = Q(form_sub_typ_id=form_sub_typ)

    q_season = Q()
    if form_typ == "field" or form_typ == "pit":
        current_season = scouting.util.get_current_season()
        q_season = Q(scout_question_flow__season=current_season)

    flows = Flow.objects.filter(q_id & q_form_typ & q_form_sub_typ & q_season & Q(void_ind ="n")).order_by("form_sub_typ_id", "name")

    parsed = []
    for flow in flows:
        parsed.append(format_flow_values(flow))

    return parsed


def save_flow(data):
    if data.get("id", None) is not None:
        flow = Flow.objects.get(id=data["id"])
    else:
        flow = Flow()

    flow.name = data["name"]
    flow.single_run = data["single_run"]
    flow.form_typ_id = data["form_typ"]["form_typ"]
    if data.get("form_sub_typ", None) is not None:
        flow.form_sub_typ_id = data["form_sub_typ"]["form_sub_typ"]

    flow.void_ind = data.get("void_ind", "n")
    flow.save()

    ids = []
    for data_question_flow in data.get("question_flows", []):
        if data_question_flow.get("id", None) is None:
            question_flow = QuestionFlow(flow=flow, question_id=data_question_flow["question"]["id"])
        else:
            question_flow = QuestionFlow.objects.get(id=data_question_flow["id"])

        question_flow.order = data_question_flow["order"]

        question_flow.save()

        save_question(data_question_flow["question"])

        ids.append(question_flow.id)

    # void questions no longer in flow
    QuestionFlow.objects.filter(Q(flow=flow) & Q(void_ind="n") & ~Q(id__in=ids)).update(void_ind="y")

    #Create link to season if does not exist
    if data["form_typ"]["form_typ"] in ["pit", "field"]:
        try:
            flow.scout_question_flow.get(void_ind="n")
        except scouting.models.QuestionFlow.DoesNotExist:
            scouting.models.QuestionFlow(flow=flow, season=scouting.util.get_current_season()).save()

    return flow
