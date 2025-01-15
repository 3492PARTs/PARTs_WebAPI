from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Lower
import cloudinary

import alerts.util
import form.models
import scouting.models
import scouting.util
import user.util
from form.models import (
    FormType,
    Question,
    Response,
    QuestionAnswer,
    QuestionOption,
    FormSubType,
    QuestionType,
    QuestionAggregate,
    QuestionAggregateType,
    QuestionCondition, QuestionFlow,
)
from scouting.models import Match, Season, ScoutField, ScoutPit, Event


def get_questions(form_typ: str, active: str = "", form_sub_typ: str = ""):
    questions = []
    season = Q()
    active_ind = Q()
    form_sub_typ_q = Q()

    if form_typ == "field" or form_typ == "pit":
        current_season = scouting.util.get_current_season()
        scout_questions = scouting.models.Question.objects.filter(
            Q(void_ind="n") & Q(season=current_season)
        )
        season = Q(question_id__in=set(sq.question_id for sq in scout_questions))

    if active != "":
        active_ind = Q(active=active)

    if form_sub_typ is None:
        form_sub_typ_q = Q(form_sub_typ_id__isnull=True)
    elif form_sub_typ != "":
        form_sub_typ_q = Q(form_sub_typ_id=form_sub_typ)

    qs = (
        Question.objects.prefetch_related("questionoption_set")
        .filter(
            season
            & Q(form_typ_id=form_typ)
            & form_sub_typ_q
            & active_ind
            & Q(void_ind="n")
        )
        .order_by("form_sub_typ__order", "order")
    )

    for q in qs:
        questions.append(format_question_values(q))

    return questions


def format_question_values(q: Question):
    # Scout question type
    try:
        sqt = q.question_typ.scout_question_type.get(void_ind="n")
        scout_question_type = {
            "id": sqt.id,
            "scorable": sqt.scorable
        }
    except scouting.models.QuestionType.DoesNotExist:
        scout_question_type = None

    # Question Type
    question_type = {
        "question_typ": q.question_typ.question_typ,
        "question_typ_nm": q.question_typ.question_typ_nm,
        "is_list": q.question_typ.is_list,
        "scout_question_type": scout_question_type
    }

    # Scout Question
    try:
        sq = q.scout_question.get(Q(void_ind="n"))

        scout_question = {
            "id": sq.id,
            "question_id": sq.question_id,
            "season_id": sq.season.season_id,
            "x": sq.x,
            "y": sq.y,
            "width": sq.width,
            "height": sq.height,
            "icon": sq.icon,
            "value_multiplier": sq.value_multiplier,
        }
        season = sq.season.season_id
    except scouting.models.Question.DoesNotExist as e:
        scout_question = None
        season = None

    # List of options if applicable
    questionoption_set = []
    for qo in q.questionoption_set.filter(void_ind="n"):
        questionoption_set.append(
            {
                "question_opt_id": qo.question_opt_id,
                "question_id": qo.question_id,
                "option": qo.option,
                "active": qo.active,
            }
        )

    # Flag if question is condition of another
    try:
        q.condition_question_to.get(Q(void_ind="n") & Q(active="y"))
        is_condition = "y"
    except QuestionCondition.DoesNotExist:
        is_condition = "n"

    return {
        "question_id": q.question_id,
        "question_flow_id": q.question_flow.id if q.question_flow is not None else None,
        "season_id": season,
        "question": q.question,
        "table_col_width": q.table_col_width,
        "order": q.order,
        "required": q.required,
        "active": q.active,
        "question_typ": question_type,
        "form_typ": q.form_typ,
        "form_sub_typ": q.form_sub_typ,
        "questionoption_set": questionoption_set,
        "display_value": f"{'' if q.active == 'y' else 'Deactivated: '} Order: {q.order}: {q.form_sub_typ.form_sub_nm + ': ' if q.form_sub_typ is not None else ''}{q.question}",
        "scout_question": scout_question,
        "is_condition": is_condition,
    }


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

    q.question_flow_id = question.get("question_flow_id", None)

    q.save()

    if question["form_typ"]["form_typ"] in ["pit", "field"]:
        if question.get("scout_question", None).get("id", None) is not None:
            sq = scouting.models.Question.objects.get(
                Q(void_ind="n") & Q(question_id=q.question_id)
            )
        else:
            sq = scouting.models.Question(question_id=q.question_id)

        if sq.season is None:
            sq.season = current_season

        scout_question = question.get("scout_question", None)
        sq.x = scout_question.get("x", None)
        sq.y = scout_question.get("y", None)
        sq.width = scout_question.get("width", None)
        sq.height = scout_question.get("height", None)
        sq.icon = scout_question.get("icon", None)
        sq.value_multiplier = scout_question.get("value_multiplier", False)
        sq.save()

    if question.get("question_id", None) is None:
        # If adding a new question we need to make a null answer for it for all questions already answered
        match question["form_typ"]["form_typ"]:
            case "pit":
                pit_responses = ScoutPit.objects.filter(
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
                field_responses = ScoutField.objects.filter(
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
            QuestionAnswer(
                response=qa, question=q, answer="!EXIST", void_ind="n"
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


def save_question_answer(answer: str, question: Question, response: Response):
    qa = QuestionAnswer(
        question=question, answer=answer, response=response, void_ind="n"
    )
    qa.save()
    return qa


def save_or_update_question_answer(question, response: Response):
    # Get answer to update or save new
    try:
        spa = QuestionAnswer.objects.get(
            Q(response=response)
            & Q(question_id=question.get("question_id", None))
            & Q(void_ind="n")
        )
        spa.answer = question.get("answer", "")
        spa.save()
    except QuestionAnswer.DoesNotExist:
        save_question_answer(
            question.get("answer", ""),
            Question.objects.get(question_id=question["question_id"]),
            response,
        )


def save_or_update_question_with_conditions_answer(question, response: Response):
    # Get answer to update or save new
    save_or_update_question_answer(question, response)

    # Save answers to any condition questions
    for c in question.get("conditions", []):
        # Get answer to update or save new
        save_or_update_question_answer(c["question_to"], response)


def get_response(response_id: int):
    res = Response.objects.get(Q(response_id=response_id) & Q(void_ind="n"))
    questions = get_questions(res.form_typ, "y")

    for question in questions:
        question["answer"] = get_response_question_answer(res, question["question_id"])

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
                res, question["question_id"]
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
        answer = QuestionAnswer.objects.get(
            Q(question_id=question_id) & Q(response=response) & Q(void_ind="n")
        ).answer
    except QuestionAnswer.DoesNotExist:
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
            questions__question_id__in=set(sq.question_id for sq in scout_questions)
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
        ~Q(question_id__in=set(q.question_id for q in questions))
    )
    for r in remove:
        qa.questions.remove(r)

    qa.save()

    return qa


def get_question_condition(form_typ: str):
    question_aggregates = []
    season = Q()

    if form_typ == "field" or form_typ == "pit":
        current_season = Season.objects.get(current="y")
        scout_questions = scouting.models.Question.objects.filter(
            Q(void_ind="n") & Q(season=current_season)
        )
        season = Q(
            question_from__question_id__in=set(q.question_id for q in scout_questions)
        )

    question_conditions = QuestionCondition.objects.filter(
        Q(void_ind="n") & Q(question_from__form_typ=form_typ) & season
    )

    for qc in question_conditions:
        question_aggregates.append(
            {
                "question_condition_id": qc.question_condition_id,
                "condition": qc.condition,
                "question_from": format_question_values(qc.question_from),
                "question_to": format_question_values(qc.question_to),
                "active": qc.active,
            }
        )

    return question_aggregates


def save_question_condition(data):
    if data.get("question_condition_id", None) is not None:
        qc = QuestionCondition.objects.get(
            question_condition_id=data["question_condition_id"]
        )
    else:
        qc = QuestionCondition()

    qc.condition = data["condition"]
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


def get_questions_with_conditions(
        form_typ: str,
        form_sub_typ: str = "",
        active: str = "y",
):
    questions_with_conditions = []
    questions = get_questions(form_typ, active, form_sub_typ)

    for q in questions:
        # Only process the ones that are not conditions, because the conditions will be in their Question FROM - see below loop
        if q["is_condition"] == "n":
            q["conditions"] = []
            question = Question.objects.get(question_id=q["question_id"])

            """ 
                Question conditions FROM will have multiple entries in the condition table
                indicating that they have multiple conditions TO. A condition TO is a 
                question that shows when the condition has been met on the question FROM
                So this loop gets all the conditions that could show for a question.

            """
            for qc in question.condition_question_from.filter(
                    Q(void_ind="n") & Q(active="y") & Q(question_to__active="y")
            ):
                q["conditions"].append(format_question_condition_values(qc))

            questions_with_conditions.append(q)

    return questions_with_conditions


def get_question_with_conditions_response_answers(response: Response):
    answers = []

    questions = get_questions_with_conditions(response.form_typ.form_typ)

    for question in questions:
        try:
            spa = QuestionAnswer.objects.get(
                Q(response=response) & Q(question_id=question["question_id"])
            )
        except QuestionAnswer.DoesNotExist as e:
            spa = QuestionAnswer(answer="")

        question["answer"] = spa.answer

        for c in question.get("conditions", []):
            try:
                spa = QuestionAnswer.objects.get(
                    Q(response=response)
                    & Q(question_id=c["question_to"]["question_id"])
                )
            except QuestionAnswer.DoesNotExist as e:
                spa = QuestionAnswer(answer="")

            c["question_to"]["answer"] = spa.answer

        answers.append(question)

    return answers


def save_field_response(data, user_id):
    current_event = scouting.util.get_current_event()
    # Build field scout object and check for match
    try:
        m = Match.objects.get(match_id=data.get("match_id", None))
    except Match.DoesNotExist:
        m = None

    form_type = FormType.objects.get(form_typ=data["form_typ"])

    response = form.models.Response(form_typ=form_type)
    response.save()

    sf = ScoutField(
        event=current_event,
        team_no_id=data["team"],
        match=m,
        user_id=user_id,
        response_id=response.response_id,
        void_ind="n",
    )
    sf.save()

    # Save the answers against the response object
    for d in data.get("question_answers", []):
        save_or_update_question_with_conditions_answer(d, response)

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
    return sf


def save_pit_response(data, user_id):
    current_event = scouting.util.get_current_event()

    form_type = FormType.objects.get(form_typ=data["form_typ"])
    # Build or get pit scout object
    try:
        sp = ScoutPit.objects.get(
            Q(team_no_id=data["team"]) & Q(void_ind="n") & Q(event=current_event)
        )
        response = sp.response

        if response.void_ind == "y":
            response = form.models.Response(form_typ=form_type)
            response.save()
            sp.response = response
            sp.save()
    except ScoutPit.DoesNotExist:
        response = form.models.Response(form_typ=form_type)
        response.save()

        sp = ScoutPit(
            event=current_event,
            team_no_id=data["team"],
            user_id=user_id,
            response=response,
            void_ind="n",
        )
        sp.save()

    # Save the answers against the response object
    for d in data.get("question_answers", []):
        save_or_update_question_with_conditions_answer(d, response)

    return sp


def save_answers(data):
    form_type = FormType.objects.get(form_typ=data["form_typ"])

    with transaction.atomic():
        response = form.models.Response(form_typ=form_type)
        response.save()

        # Save the answers against the response object
        for d in data.get("question_answers", []):
            save_or_update_question_with_conditions_answer(d, response)

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
            alerts.util.stage_alert_channel_send(a, acct)

def get_question_flows(form_typ=None, form_sub_typ=None):
    q_form_typ = Q()
    if form_typ is not None:
        q_form_typ = Q(form_typ_id=form_typ)

    q_form_sub_typ = Q()
    if form_sub_typ is not None:
        q_form_sub_typ = Q(form_sub_typ_id=form_sub_typ)

    qfs = QuestionFlow.objects.filter(q_form_typ & q_form_sub_typ & Q(void_ind ="n"))
    for q in qfs:
        print(q)

    return qfs

def save_question_flow(data):
    if data.get("id", None) is not None:
        qf = QuestionFlow.objects.get(id=data["id"])
    else:
        qf = QuestionFlow()

    qf.name = data["name"]
    qf.form_typ_id = data["form_typ"]["form_typ"]
    if data.get("form_sub_typ", None) is not None:
        qf.form_sub_typ_id = data["form_sub_typ"]["form_sub_typ"]
    qf.save()
    return qf
