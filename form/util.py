from django.conf import settings
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import Lower

import json

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
    QuestionConditionType, FlowCondition, FlowQuestion, GraphType, Graph, GraphCategory, GraphQuestion, GraphBin, GraphCategoryAttribute, GraphQuestionType
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
        .prefetch_related("questionoption_set", "scout_question", "question_typ", "condition_question_from", "condition_question_to", "flowquestion_set")
        .annotate(
            in_flow=Exists(
                FlowQuestion.objects.filter(Q(question_id=OuterRef("pk")) & Q(active="y") & Q(void_ind="n"))
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

    # Question Type
    question_type = {
        "question_typ": in_question.question_typ.question_typ,
        "question_typ_nm": in_question.question_typ.question_typ_nm,
        "is_list": in_question.question_typ.is_list,
    }

    # Scout Question
    try:
        sq = in_question.scout_question.get(Q(void_ind="n"))

        scout_question = {
            "id": sq.id,
            "question_id": sq.id,
            "season_id": sq.season.id,
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

    flow_questions = in_question.flowquestion_set.filter(Q(active="y") & Q(void_ind="n"))

    return {
        "id": in_question.id,
        "flow_id_set": set(qf.flow.id for qf in flow_questions),
        "season_id": season,
        "question": in_question.question,
        "table_col_width": in_question.table_col_width,
        "order": in_question.order,
        "required": in_question.required,
        "svg": in_question.svg,
        "x": in_question.x,
        "y": in_question.y,
        "width": in_question.width,
        "height": in_question.height,
        "icon": in_question.icon,
        "icon_only": in_question.icon_only,
        "value_multiplier": in_question.value_multiplier,
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


def save_question(data):
    current_season = None
    if data["form_typ"]["form_typ"] in ["pit", "field"]:
        current_season = scouting.util.get_current_season()

    required = data.get("required", "n")
    required = required if required != "" else "n"

    if data.get("id", None) is not None:
        question = Question.objects.get(id=data["id"])
        question.question = data["question"]
        question.table_col_width = data["table_col_width"]
        question.question_typ_id = data["question_typ"]["question_typ"]
        question.order = data["order"]
        question.required = required
        question.active = data["active"]
    else:
        question = Question(
            question_typ_id=data["question_typ"]["question_typ"],
            form_typ_id=data["form_typ"]["form_typ"],
            question=data["question"],
            table_col_width=data["table_col_width"],
            order=data["order"],
            active=data["active"],
            required=required,
            void_ind="n",
        )

    question.form_sub_typ_id = None if data.get("form_sub_typ", None) is None else data["form_sub_typ"].get("form_sub_typ", None)
    question.x = data.get("x", None)
    question.y = data.get("y", None)
    question.width = data.get("width", None)
    question.height = data.get("height", None)
    question.icon = data.get("icon", None)
    question.icon_only = data.get("icon_only", False)
    question.value_multiplier = data.get("value_multiplier", None)
    question.svg = data.get("svg", None)

    for qfid in data.get("question_flow_id_set", []):
        question.question_flow.add(Flow.objects.get(id=qfid))

    question.save()

    if data["form_typ"]["form_typ"] in ["pit", "field"]:
        if data.get("scout_question", None).get("id", None) is not None:
            sq = scouting.models.Question.objects.get(id=data["scout_question"]["id"])
        else:
            sq = scouting.models.Question(question=question)

        if sq.season is None:
            sq.season = current_season

        sq.save()

    if data.get("id", None) is None:
        # If adding a new question we need to make a null answer for it for all questions already answered
        match data["form_typ"]["form_typ"]:
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
                    Q(void_ind="n") & Q(form_typ_id=data["form_typ"])
                )

        for qa in questions_answered:
            Answer(
                response=qa, question=question, value="!EXIST", void_ind="n"
            ).save()

    if (
            data["question_typ"]["is_list"] == "y"
            and len(data.get("questionoption_set", [])) <= 0
    ):
        raise Exception("Select questions must have options.")

    for op in data.get("questionoption_set", []):
        if op.get("question_opt_id", None) is not None:
            qop = QuestionOption.objects.get(question_opt_id=op["question_opt_id"])
            qop.option = op["option"]
            qop.active = op["active"]
        else:
            qop = QuestionOption(
                option=op["option"], question=question, active=op["active"], void_ind="n"
            )

        qop.save()


def get_question_types():
    qts = QuestionType.objects.filter(void_ind="n").order_by(
        Lower("question_typ_nm")
    )
    question_types = []

    for qt in qts:

        question_types.append({
            "question_typ": qt.question_typ,
            "question_typ_nm": qt.question_typ_nm,
            "is_list": qt.is_list,
        })

    return question_types


def get_form_sub_types(form_typ: str):
    sub_types = FormSubType.objects.filter(form_typ=form_typ).order_by(
        "order", Lower("form_sub_nm")
    )
    return sub_types


def save_or_update_answer(data, response: Response):
    q_question = Q(question_id=-99)
    if data.get("question", None) is not None:
        q_question = Q(question_id=data["question"]["id"])

    #q_question_flow = Q()
    #if data.get("flow", None) is not None:
    #    q_question_flow = Q(flow_id=data["flow"]["id"])
    # flows are not unique this causes them all to save under a single answer

    if data.get("question", None) is None and data.get("flow", None) is None:
        raise Exception("No question or flow")

    # Get answer to update or save new
    try:
        answer = Answer.objects.get(
            Q(response=response)
            & q_question
            #& q_question_flow
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
            questions__in=[sq.question for sq in scout_questions]
        )

    qas = QuestionAggregate.objects.filter(
        Q(void_ind="n") & Q(questions__form_typ=form_typ) & season
    ).distinct()
    for qa in qas:
        question_aggregates.append(
            parse_question_aggregate(qa)
        )

    return question_aggregates


def parse_question_aggregate(question_aggregate: QuestionAggregate):
    return {
        "id": question_aggregate.id,
        "name": question_aggregate.name,
        "horizontal": question_aggregate.horizontal,
        "question_aggregate_typ": question_aggregate.question_aggregate_typ,
        "questions": list(
            format_question_values(q)
            for q in question_aggregate.questions.filter(Q(void_ind="n") & Q(active="y"))
        ),
        "active": question_aggregate.active,
    }


def get_question_aggregate_types():
    return QuestionAggregateType.objects.filter(Q(void_ind="n"))


def save_question_aggregate(data):
    if data.get("id", None) is not None:
        qa = QuestionAggregate.objects.get(
            Q(id=data["id"])
        )
    else:
        qa = QuestionAggregate()

    qa.name = data["name"]
    qa.horizontal = data["horizontal"]
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
        id__in=set(q["id"] for q in data["questions"])
    )

    for q in questions:
        qa.questions.add(q)

    qa.save()

    remove = qa.questions.filter(
        ~Q(id__in=set(q.id for q in questions))
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

    qc.question_from_id = data["question_from"]["id"]
    qc.question_to_id = data["question_to"]["id"]

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


def save_flow_condition(data):
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
            "flow_questions": [{
                "id": qf.id,
                "flow_id": flow.id,
                "question": format_question_values(qf.question),
                "order": qf.order,
                "active": qf.active
            } for qf in FlowQuestion.objects.filter(Q(flow=flow) & Q(active="y") & Q(question__void_ind="n")& Q(question__active="y") & Q(void_ind="n")).order_by("order", "question__question")],
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

    sub_types = FormSubType.objects.filter(form_typ=form_type).order_by("order")
    for st in sub_types:
        qs = get_questions("field", "y", st.form_sub_typ, not_in_flow=True)
        qfs = get_flows(form_typ="field", form_sub_typ=st.form_sub_typ)

        form_parsed["form_sub_types"].append({
            "form_sub_typ": st,
            "questions": qs,
            "flows": qfs
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
    for data_flow_question in data.get("flow_questions", []):
        if data_flow_question.get("id", None) is None:
            question_flow = FlowQuestion(flow=flow, question_id=data_flow_question["question"]["id"])
        else:
            question_flow = FlowQuestion.objects.get(id=data_flow_question["id"])

        question_flow.order = data_flow_question["order"]

        question_flow.save()

        save_question(data_flow_question["question"])

        ids.append(question_flow.id)

    # void questions no longer in flow
    FlowQuestion.objects.filter(Q(flow=flow) & Q(void_ind="n") & ~Q(id__in=ids)).update(void_ind="y")

    #Create link to season if does not exist
    if data["form_typ"]["form_typ"] in ["pit", "field"]:
        try:
            flow.scout_question_flow.get(void_ind="n")
        except scouting.models.QuestionFlow.DoesNotExist:
            scouting.models.QuestionFlow(flow=flow, season=scouting.util.get_current_season()).save()

    return flow


def get_graph_types():
    return GraphType.objects.filter(Q(void_ind="n"))


def get_graph_question_types():
    return GraphQuestionType.objects.filter(Q(void_ind="n"))


def parse_graph_category(graph_category: GraphCategory):
    return {
        "id": graph_category.id,
        "graph_id": graph_category.graph.id,
        "category": graph_category.category,
        "order": graph_category.order,
        "active": graph_category.active,
        "graphcategoryattribute_set": [parse_graph_category_attribute(gc) for gc in graph_category.graphcategoryattribute_set.filter(Q(void_ind="n") & Q(active="y"))]
    }


def parse_graph_category_attribute(graph_category_attribute: GraphCategoryAttribute):
    return {
        "id": graph_category_attribute.id,
        "graph_category_id": graph_category_attribute.graph_category.id,
        "question": format_question_values(graph_category_attribute.question),
        "question_condition_typ": graph_category_attribute.question_condition_typ,
        "value": graph_category_attribute.value,
        "active": graph_category_attribute.active
    }


def parse_graph_question(graph_question: GraphQuestion):
    return {
        "id": graph_question.id,
        "graph_id": graph_question.graph.id,
        "question": format_question_values(graph_question.question) if graph_question.question is not None else None,
        "question_aggregate": parse_question_aggregate(graph_question.question_aggregate) if graph_question.question_aggregate is not None else None,
        "graph_question_typ": graph_question.graph_question_typ,
        "active": graph_question.active
    }


def get_graphs(for_current_season=False, graph_id=None):
    q_season = Q()
    if for_current_season:
        current_season = scouting.util.get_current_season()

        q_season = Q(Q(scout_graph__season=current_season) & Q(scout_graph__void_ind="n"))

    q_graph_id = Q()
    if graph_id is not None:
        q_graph_id = Q(id=graph_id)

    graphs = Graph.objects.filter(q_graph_id & q_season & Q(void_ind="n") & Q(active="y"))

    parsed = []
    for graph in graphs:
        parsed.append({
            "id": graph.id,
            "graph_typ": graph.graph_typ,
            "name": graph.name,
            "scale_x": graph.scale_x,
            "scale_y": graph.scale_y,
            "active": graph.active,
            "graphbin_set": graph.graphbin_set.filter(Q(void_ind="n") & Q(active="y")).order_by("bin"),
            "graphcategory_set": [parse_graph_category(graph_category) for graph_category in graph.graphcategory_set.filter(Q(void_ind="n") & Q(active="y")).order_by("order")],
            "graphquestion_set":[parse_graph_question(graph_question) for graph_question in graph.graphquestion_set.filter(Q(void_ind="n") & Q(active="y"))],
        })

    return parsed


def save_graph(data, user_id, for_current_season=False):
    with transaction.atomic():
        if data.get("id", None) is None:
            graph = Graph(creator_id=user_id)
        else:
            graph = Graph.objects.get(id=data["id"])

        graph.graph_typ_id = data["graph_typ"]["graph_typ"]
        graph.name = data["name"]
        graph.scale_x = data["scale_x"]
        graph.scale_y = data["scale_y"]
        graph.active = data["active"]

        graph.save()

        if for_current_season:
            try:
                scouting.models.Graph.objects.get(Q(graph=graph) & Q(void_ind="n"))
            except scouting.models.Graph.DoesNotExist:
                scouting.models.Graph(season=scouting.util.get_current_season(), graph=graph).save()


        if graph.graph_typ.requires_bins:
            bins_data = data.get("graphbin_set", [])
            if len(bins_data) <= 0:
                raise Exception("No bins provided")

            for bin_data in bins_data:
                if bin_data.get("id", None) is None:
                    graph_bin = GraphBin()
                else:
                    graph_bin = GraphBin.objects.get(id=bin_data["id"])

                graph_bin.graph = graph
                graph_bin.bin = bin_data["bin"]
                graph_bin.width = bin_data["width"]
                graph_bin.active = bin_data["active"]

                graph_bin.save()

        if graph.graph_typ.requires_categories:
            categories_data = data.get("graphcategory_set", [])
            if len(categories_data) <= 0:
                raise Exception("No categories provided")

            for category_data in categories_data:
                if category_data.get("id", None) is None:
                    category = GraphCategory()
                else:
                    category = GraphCategory.objects.get(id=category_data["id"])

                category.graph = graph
                category.category = category_data["category"]
                category.order = category_data["order"]
                category.active = category_data["active"]

                category.save()

                category_attributes_data = category_data.get("graphcategoryattribute_set", [])
                if len(category_attributes_data) <= 0:
                    raise Exception("No category attribute(s) provided")

                for category_attribute_data in category_attributes_data:
                    if category_attribute_data.get("id", None) is None:
                        category_attribute = GraphCategoryAttribute()
                    else:
                        category_attribute = GraphCategoryAttribute.objects.get(id=category_attribute_data["id"])

                    category_attribute.graph_category = category

                    question_condition_typ = category_attribute_data.get("question_condition_typ", None)
                    question = category_attribute_data.get("question", None)
                    question_aggregate = category_attribute_data.get("question_aggregate", None)

                    if question is None and question_aggregate is None:
                        raise Exception("No question or aggregate")

                    category_attribute.question_id = None if question is None else question.get("id", None)
                    category_attribute.question_aggregate = None if question_aggregate is None else question_aggregate.get("id", None)
                    category_attribute.question_condition_typ_id = None if question_condition_typ is None else question_condition_typ.get("question_condition_typ", None)
                    category_attribute.value = category_attribute_data["value"]
                    category_attribute.active = category_attribute_data["active"]

                    category_attribute.save()

        requirements = []
        for required_graph_question_typ in data["graph_typ"]["requires_graph_question_typs"]:
            requirements.append({
                "graph_question_typ": required_graph_question_typ["graph_question_typ"],
                "found": False
            })

        for graph_question_data in data.get("graphquestion_set", []):
            if graph_question_data.get("graph_question_typ", None) is not None:
                requirement = [req for req in requirements if req["graph_question_typ"] == graph_question_data["graph_question_typ"]["graph_question_typ"]]
                if len(requirement) > 0:
                    requirement[0]["found"] = True

            if graph_question_data.get("id", None) is None:
                graph_question = GraphQuestion()
            else:
                graph_question = GraphQuestion.objects.get(id=graph_question_data["id"])

            graph_question.graph = graph

            graph_question_typ = graph_question_data.get("graph_question_typ", None)
            question = graph_question_data.get("question", None)
            question_aggregate = graph_question_data.get("question_aggregate", None)

            if question is None and question_aggregate is None:
                raise Exception("No question or aggregate")

            graph_question.graph_question_typ_id = None if graph_question_typ is None else graph_question_typ.get("graph_question_typ", None)
            graph_question.question_id = None if question is None else question.get("id", None)
            graph_question.question_aggregate_id = None if question_aggregate is None else question_aggregate.get("id", None)
            graph_question.active = graph_question_data["active"]

            graph_question.save()

        for requirement in requirements:
            if not requirement["found"]:
                raise Exception(f"Missing graph question requirement: {requirement['graph_question_typ']}")


def graph_responses(graph_id, responses, aggregate_responses=None):
    graph = get_graphs(graph_id=graph_id)[0]

    data = None
    match graph["graph_typ"].graph_typ:
        case "histogram":
            all_bins = []

            for graph_question in graph["graphquestion_set"]:
                question_bins = {
                    "label": graph_question["question"]["question"] if graph_question["question"] is not None else graph_question["question_aggregate"]["name"],
                    "bins": []
                }
                all_bins.append(question_bins)

                for gb in graph["graphbin_set"]:
                    graph_bin = {
                        "bin": int(gb.bin),
                        "width": int(gb.width),
                        "count": 0
                    }

                    if graph_question["question"] is not None:
                        question = graph_question["question"]
                        answers = Answer.objects.filter(
                            Q(response__in=responses) &
                            (
                                    Q(question_id=question["id"]) |
                                    Exists(FlowAnswer.objects.filter(Q(question_id=question["id"]) & Q(answer_id=OuterRef("pk")) & Q(void_ind="n")))
                             ) &
                            Q(void_ind="n")).order_by("response__time")

                        for answer in answers:
                            if answer.question is not None:
                                value = int(answer.value)

                                if question["value_multiplier"] is not None:
                                    value *= int(question["value_multiplier"])

                                if graph_bin["bin"] <= value < graph_bin["bin"] + graph_bin["width"]:
                                    graph_bin["count"] += 1

                            if answer.flow is not None:
                                flow_answers = answer.flowanswer_set.filter(Q(question_id=question["id"]) & Q(void_ind="n")).order_by("value_time")

                                for flow_answer in flow_answers:
                                    value = 1

                                    if question["value_multiplier"] is not None:
                                        value *= int(question["value_multiplier"])

                                    if graph_bin["bin"] <= value < graph_bin["bin"] + graph_bin["width"]:
                                        graph_bin["count"] += 1
                    # based on a question aggregate
                    else:
                        questions = graph_question["question_aggregate"]["questions"]

                        for response in responses:
                            aggregate = aggregate_answers_horizontally(graph_question["question_aggregate"]["question_aggregate_typ"].question_aggregate_typ, response, set(question["id"] for question in questions))

                            if graph_bin["bin"] <= aggregate < graph_bin["bin"] + graph_bin["width"]:
                                graph_bin["count"] += 1
                    graph_bin["bin"] = f"{graph_bin['bin']} - {graph_bin['bin'] + graph_bin['width'] - 1}"
                    question_bins["bins"].append(graph_bin)
            data = all_bins
        case "ctg-histgrm":
            categories = []
            for graph_category in graph["graphcategory_set"]:
                categories.append({
                    "id": graph_category["id"],
                    "bin": graph_category["category"],
                    "graphcategoryattribute_set": graph_category["graphcategoryattribute_set"],
                    "count": 0
                })

            # go response by response to find which match a catrgory
            for response in responses:
                # process categories and see which answers pass it
                for category in categories:
                    passed_category = True
                    for category_attribute in category["graphcategoryattribute_set"]:

                        # category attribute is based on a question
                        if category_attribute["question"] is not None:
                            #check regular question answers
                            answers = Answer.objects.filter(Q(response=response) & Q(void_ind="n") & Q(question_id=category_attribute["question"]["id"])).order_by("response__time")

                            for answer in answers:
                                if answer.question is not None:
                                    value = answer.value

                                    if answer.question.value_multiplier is not None:
                                        value = int(value) * int(answer.question.value_multiplier)

                                    passed_category = passed_category and is_question_condition_passed(category_attribute["question_condition_typ"].question_condition_typ, value, category_attribute["value"])


                            # check flow answers, they need combined as they span the whole match
                            flow_answers = FlowAnswer.objects.filter(Q(question_id=category_attribute["question"]["id"]) & Q(void_ind="n") & Q(answer__response=response)).order_by("value_time")

                            if len(flow_answers) <= 0:
                                passed_category = False

                            value = 0
                            for flow_answer in flow_answers:
                                if flow_answer.question.question_typ.question_typ == "mnt-psh-btn":
                                    value += 1
                                else:
                                    raise Exception("not accounted for yet")
                                    value = flow_answer.value

                                if flow_answer.question.value_multiplier is not None:
                                    value *= int(flow_answer.question.value_multiplier)

                            passed_category = passed_category and is_question_condition_passed(
                                category_attribute["question_condition_typ"].question_condition_typ, value,
                                category_attribute["value"])

                        # category attribute is based on a question aggregate
                        else:
                            aggregate = aggregate_answers_horizontally(category_attribute["question_aggregate"].question_aggregate_typ.question_aggregate_typ, response, set(question["id"] for question in category_attribute["question_aggregate"]["questions"]))

                            passed_category = passed_category and is_question_condition_passed(
                                category_attribute["question_condition_typ"].question_condition_typ, aggregate,
                                category_attribute["value"])

                    # passes attribute, stop processing and move onto next response.
                    if passed_category:
                        category["count"] += 1
                        break
            data = categories
        case "res-plot":
            plot = []
            ref_pt = [gq for gq in graph["graphquestion_set"] if gq["graph_question_typ"] is not None and gq["graph_question_typ"].graph_question_typ == 'ref-pnt'][0]
            aggregate = aggregate_answers_vertically(ref_pt["question_aggregate"]["question_aggregate_typ"].question_aggregate_typ, responses if aggregate_responses is None else aggregate_responses, set(q["id"] for q in ref_pt["question_aggregate"]["questions"]))
            graph_questions = [gq for gq in graph["graphquestion_set"] if gq["graph_question_typ"] is None]

            for graph_question in graph_questions:
                plot_entry = {
                    "label": graph_question["question"]["question"] if graph_question["question"] is not None else graph_question["question_aggregate"]["name"],
                    "points": []
                }
                plot.append(plot_entry)

                # go response by response to compute difference
                for response in responses:
                    if graph_question["question"] is not None:
                        question = graph_question["question"]
                        # check regular question answers
                        try:
                            answer = Answer.objects.get(Q(response=response) & Q(void_ind="n") & Q(
                                question_id=question["id"])).order_by("response__time")

                            value = int(answer.value)

                            if answer.question.value_multiplier is not None:
                                value *= int(answer.question.value_multiplier)

                            plot_entry["points"].append({
                                "point": value - aggregate,
                                "time": answer.time
                            })
                        except Answer.DoesNotExist:
                            pass

                        # check flow answers, they need combined as they span the whole match
                        flow_answers = FlowAnswer.objects.filter(
                            Q(question_id=question["id"]) & Q(void_ind="n") & Q(
                                answer__response=response)).order_by("value_time")

                        value = 0
                        time = None
                        for flow_answer in flow_answers:
                            time = flow_answer.answer.response.time

                            if flow_answer.question.question_typ.question_typ == "mnt-psh-btn":
                                value += 1
                            else:
                                raise Exception("not accounted for yet")
                                value = flow_answer.value

                            if flow_answer.question.value_multiplier is not None:
                                value *= int(flow_answer.question.value_multiplier)

                        if len(flow_answers) > 0:
                            plot_entry["points"].append({
                                "point": value - aggregate,
                                "time": time
                            })

                    # based on a question aggregate
                    else:
                        aggregate_value = aggregate_answers_horizontally(category_attribute["question_aggregate"].question_aggregate_typ.question_aggregate_typ, response, set(question["id"] for question in graph_question["question_aggregate"]["questions"]))
                        plot_entry["points"].append({
                            "point": aggregate_value - aggregate,
                            "time": field_response.time
                        })

            data = plot
        case "diff-plot":
            plot = []
            for graph_question in graph["graphquestion_set"]:
                plot_entry = {
                    "label": graph_question["question"]["question"] if graph_question["question"] is not None else graph_question["question_aggregate"]["name"],
                    "points": []
                }
                plot.append(plot_entry)

                # go response by response to compute difference
                previous = None
                for response in responses:
                    if graph_question["question"] is not None:
                        question = graph_question["question"]
                        # check regular question answers
                        try:
                            answer = Answer.objects.get(Q(response=response) & Q(void_ind="n") & Q(
                                question_id=question["id"])).order_by("response__time")

                            value = int(answer.value)

                            if answer.question.value_multiplier is not None:
                                value *= int(answer.question.value_multiplier)

                        except Answer.DoesNotExist:
                            pass

                        # check flow answers, they need combined as they span the whole match
                        flow_answers = FlowAnswer.objects.filter(
                            Q(question_id=question["id"]) & Q(void_ind="n") & Q(
                                answer__response=response)).order_by("value_time")

                        value = 0
                        for flow_answer in flow_answers:

                            if flow_answer.question.question_typ.question_typ == "mnt-psh-btn":
                                value += 1
                            else:
                                raise Exception("not accounted for yet")
                                value = flow_answer.value

                            if flow_answer.question.value_multiplier is not None:
                                value *= int(flow_answer.question.value_multiplier)
                    # based on a question aggregate
                    else:
                        value = aggregate_answers_horizontally(
                            category_attribute["question_aggregate"].question_aggregate_typ.question_aggregate_typ,
                            response,
                            set(question["id"] for question in graph_question["question_aggregate"]["questions"]))

                    plot_entry["points"].append({
                        "point": previous - value if previous is not None else 0,
                        "time": response.time
                    })
                    previous = value

            data = plot
        case "box-wskr":
            plot = []

            for graph_question in graph["graphquestion_set"]:
                plot_entry = {
                    "label": graph_question["question"]["question"] if graph_question["question"] is not None else graph_question["question_aggregate"]["name"],
                    "dataset": [],
                }


                # go response by response to compute difference
                for response in responses:
                    if graph_question["question"] is not None:
                        question = graph_question["question"]
                        # check regular question answers
                        try:
                            answer = Answer.objects.get(Q(response=response) & Q(void_ind="n") & Q(
                                question_id=question["id"])).order_by("response__time")

                            value = int(answer.value)

                            if answer.question.value_multiplier is not None:
                                value *= int(answer.question.value_multiplier)

                        except Answer.DoesNotExist:
                            pass

                        # check flow answers, they need combined as they span the whole match
                        flow_answers = FlowAnswer.objects.filter(
                            Q(question_id=question["id"]) & Q(void_ind="n") & Q(
                                answer__response=response)).order_by("value_time")

                        value = 0
                        for flow_answer in flow_answers:

                            if flow_answer.question.question_typ.question_typ == "mnt-psh-btn":
                                value += 1
                            else:
                                raise Exception("not accounted for yet")
                                value = flow_answer.value

                            if flow_answer.question.value_multiplier is not None:
                                value *= int(flow_answer.question.value_multiplier)
                    # based on a question aggregate
                    else:
                        value = aggregate_answers_horizontally(
                            category_attribute["question_aggregate"].question_aggregate_typ.question_aggregate_typ,
                            response,
                            set(question["id"] for question in graph_question["question_aggregate"]["questions"]))

                    plot_entry["dataset"].append(value)

                # sort data to build box and whisker plot
                if len(plot_entry["dataset"]) > 0:
                    plot_entry["dataset"].sort()
                    quartiles = compute_quartiles(plot_entry["dataset"])
                    plot_entry["q1"] = quartiles["Q1"]
                    plot_entry["q2"] = quartiles["Q2"]
                    plot_entry["q3"] = quartiles["Q3"]
                    plot_entry["min"] = plot_entry["dataset"][0]
                    plot_entry["max"] = plot_entry["dataset"][len(plot_entry["dataset"]) - 1]
                    plot.append(plot_entry)

            data = plot
        case "ht-map":
            maps = []

            for graph_question in graph["graphquestion_set"]:
                map_entry = {
                    "question": graph_question["question"],
                    "points": [],
                }

                # go response by response to compute difference
                for response in responses:
                    if graph_question["question"] is not None:
                        question = graph_question["question"]
                        # check regular question answers
                        try:
                            answer = Answer.objects.get(Q(response=response) & Q(void_ind="n") & Q(
                                question_id=question["id"])).order_by("response__time")

                            if answer.question.question_typ.question_typ == "mnt-psh-btn":
                                map_entry["points"].append(json.loads(answer.value))
                            else:
                                raise Exception("not accounted for yet")
                                value = answer.value

                        except Answer.DoesNotExist:
                            pass

                        # check flow answers, they need combined as they span the whole match
                        flow_answers = FlowAnswer.objects.filter(
                            Q(question_id=question["id"]) & Q(void_ind="n") & Q(
                                answer__response=response)).order_by("value_time")

                        for flow_answer in flow_answers:

                            if flow_answer.question.question_typ.question_typ == "mnt-psh-btn":
                                map_entry["points"].append(json.loads(flow_answer.value))
                            else:
                                raise Exception("not accounted for yet")
                                value = flow_answer.value

                    # based on a question aggregate
                    else:
                        value = aggregate_answers_horizontally(
                            category_attribute["question_aggregate"].question_aggregate_typ.question_aggregate_typ,
                            response,
                            set(question["id"] for question in graph_question["question_aggregate"]["questions"]))

                        raise Exception("not accounted for yet")

                maps.append(map_entry)

            data = maps
    return data


def is_question_condition_passed(question_condition_typ: str, answer_value, match_value=None):
    match question_condition_typ:
        case "equal":
            return answer_value == match_value
        case "gt":
            return int(answer_value) > int(match_value)
        case "gt-equal":
            return int(answer_value) >= int(match_value)
        case "lt-equal":
            return int(answer_value) <= int(match_value)
        case "lt":
            return int(answer_value) < int(match_value)
        case "exist":
            return answer_value is not None and len(str(answer_value)) > 0
        case _:
            raise Exception("no type")


def aggregate_answers_horizontally(question_aggregate_typ: str, response: Response, question_ids):
    answers = Answer.objects.filter(
        Q(response=response) &
        (
                Q(question_id__in=question_ids) |
                Exists(FlowAnswer.objects.filter(
                    Q(question_id__in=question_ids) & Q(answer_id=OuterRef("pk")) & Q(
                        void_ind="n")))
        ) &
        Q(void_ind="n")).order_by("response__time")

    return aggregate_answers(question_aggregate_typ, answers, question_ids)


def aggregate_answers_vertically(question_aggregate_typ: str, responses, question_ids):
    answers = Answer.objects.filter(
        Q(response__in=responses) &
        (
                Q(question_id__in=question_ids) |
                Exists(FlowAnswer.objects.filter(
                    Q(question_id__in=question_ids) & Q(answer_id=OuterRef("pk")) & Q(
                        void_ind="n")))
        ) &
        Q(void_ind="n")).order_by("response__time")

    return aggregate_answers(question_aggregate_typ, answers, question_ids)


def aggregate_answers(question_aggregate_typ: str, answers, question_ids):
    summation = 0
    length = 0
    for answer in answers:
        if answer.question is not None:
            value = int(answer.value)

            if answer.question.value_multiplier is not None:
                value *= int(answer.question.value_multiplier)

            length += 1
            summation += value

        if answer.flow is not None:
            flow_answers = answer.flowanswer_set.filter(
                Q(question_id__in=question_ids) & Q(void_ind="n")).order_by(
                "value_time")

            for flow_answer in flow_answers:
                value = 1

                if flow_answer.question.value_multiplier is not None:
                    value *= int(flow_answer.question.value_multiplier)

                length += 1
                summation += value

    match question_aggregate_typ:
        case "sum":
            return summation
        case "avg":
            if length == 0:
                raise Exception("No division by 0 for aggregating averages")
            return summation/length
        case _:
            raise Exception("no type")


def compute_quartiles(data):
    """
    Computes the first, second (median), and third quartiles of a dataset.

    Args:
        data: A list of numerical data.

    Returns:
        A dictionary containing the first quartile (Q1), median (Q2), and
        third quartile (Q3). Returns an empty dictionary if the input data
        is empty. Raises a TypeError if the input is not a list or if the
        elements of the list are not numeric.
    """

    if not isinstance(data, list):
        raise TypeError("Input data must be a list.")

    if not data:  # Handle empty data case
        return {}

    for x in data:
        if not isinstance(x, (int, float)):
            raise TypeError("All elements of the list must be numeric.")

    sorted_data = sorted(data)  # Sort the data
    n = len(sorted_data)

    def _calculate_quartile(fraction):  # Helper function
        index = (n - 1) * fraction
        i = int(index)
        decimal_part = index - i

        if i < 0: #Handles edge cases where n is small.
            return sorted_data[0]
        elif i >= n -1:
            return sorted_data[-1]

        return sorted_data[i] + (sorted_data[i + 1] - sorted_data[i]) * decimal_part

    q1 = _calculate_quartile(0.25)
    q2 = _calculate_quartile(0.50)  # Median
    q3 = _calculate_quartile(0.75)

    return {"Q1": q1, "Q2": q2, "Q3": q3}
