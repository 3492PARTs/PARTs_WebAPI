from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from form.models import QuestionAggregate, QuestionAnswer, FormSubType
import scouting.util
import form
from scouting.models import EventTeamInfo, FieldResponse, FieldSchedule


def build_table_columns():
    #sqsa = form.util.get_form_questions("field", "auto")
    #sqst = form.util.get_form_questions("field", "teleop")
    #sqso = form.util.get_form_questions("field", "post")

    form_questions = form.util.get_form_questions("field")
    all_questions = []

    table_cols = [
        {
            "PropertyName": "team_no",
            "ColLabel": "Team No",
            "Width": "75px",
            "scorable": False,
            "order": 0,
        },
        {
            "PropertyName": "rank",
            "ColLabel": "Rank",
            "Width": "50px",
            "scorable": False,
            "order": 1,
        },
        {
            "PropertyName": "match",
            "ColLabel": "Match",
            "Width": "50px",
            "scorable": False,
            "order": 1,
        },
    ]

    for form_sub_type in form_questions["form_sub_types"]:
        for question in form_sub_type["questions"]:
            all_questions.append(question)
            table_cols.append(
                {
                    "PropertyName": "ans" + str(question["question_id"]),
                    "ColLabel": (
                        ""
                        if question.get("form_sub_typ", None) is None
                        else question.get("form_sub_typ").form_sub_typ[0:1].upper() + ": "
                    )
                    + (" C: " if question["question_conditional_on"] is not None else "")
                    + question["question"],
                    "Width": question["table_col_width"],
                    "order": question["order"],
                }
            )

        for question_flow in form_sub_type["question_flows"]:
            for question in question_flow["questions"]:
                all_questions.append(question)
                table_cols.append(
                    {
                        "PropertyName": "ans" + str(question["question_id"]),
                        "ColLabel": (
                            ""
                            if question.get("form_sub_typ", None) is None
                            else question.get("form_sub_typ").form_sub_typ[0:1].upper() + ": "
                        )
                        + " QF: "
                        + question["question"],
                        "Width": question["table_col_width"],
                        "order": question["order"],
                    }
                )

        question_aggregates = QuestionAggregate.objects.filter(
            Q(void_ind="n")
            & Q(active="y")
            & Q(questions__question_id__in=set(q["question_id"] for q in all_questions))
        ).distinct()
        """
        question_aggregate_count = 1
        for question_aggregate in question_aggregates:
            table_cols.append(
                {
                    "PropertyName": "ans_sqa" + str(question_aggregate.question_aggregate_id),
                    "ColLabel": (
                        ""
                        if sqs[0].get("form_sub_typ", None) is None
                        else sqs[0]["form_sub_typ"][0:1].upper() + ": "
                    )
                    + "AGG: "
                    + question_aggregate.field_name,
                    "Width": "100px",
                    "scorable": True,
                    "order": sqs[len(sqs) - 1]["order"] + question_aggregate_count,
                }
            )

            question_aggregate_count += 1
    """
    table_cols.append(
        {
            "PropertyName": "user",
            "ColLabel": "Scout",
            "Width": "100px",
            "scorable": False,
            "order": 9999999999,
        }
    )
    table_cols.append(
        {
            "PropertyName": "time",
            "ColLabel": "Time",
            "Width": "150px",
            "scorable": False,
            "order": 99999999999,
        }
    )

    return table_cols


def get_responses(request, team=None, user=None, after_date_time=None):
    table_cols = build_table_columns()

    field_scouting_responses = []

    current_season = scouting.util.get_current_season()

    current_event = scouting.util.get_current_event()

    if current_event is None:
        return scouting.util.get_no_event_ret_message(
            "scouting.field.util.get_responses", request.user.id
        )

    # Pull responses by what input
    if team is not None:
        # get response for individual team
        scout_fields = FieldResponse.objects.filter(
            Q(event=current_event) & Q(team_no_id=team) & Q(void_ind="n")
        ).order_by("-time", "-scout_field_id")
    elif user is not None:
        # get response for individual scout
        scout_fields = FieldResponse.objects.filter(
            Q(event=current_event) & Q(user=user) & Q(void_ind="n")
        ).order_by("-time", "-scout_field_id")
    elif after_date_time is not None:
        # get response for individual scout
        scout_fields = FieldResponse.objects.filter(
            Q(event=current_event) & Q(time__gt=after_date_time) & Q(void_ind="n")
        ).order_by("-time", "-scout_field_id")
    else:
        # get everything
        scout_fields = FieldResponse.objects.filter(
            Q(event=current_event) & Q(void_ind="n")
        ).order_by("-time", "-scout_field_id")

    # Loop over all the responses selected and put in table
    for scout_field in scout_fields:
        question_answers = QuestionAnswer.objects.filter(Q(response=scout_field.response) & Q(void_ind="n"))

        response = {}
        for question_answer in question_answers:
            if question_answer.question is not None:
                response[f"ans{question_answer.question_id}"] = question_answer.answer
            if question_answer.question_flow is not None:
                for qf_question in question_answer.question_flow.question_set.filter(Q(active="y") & Q(void_ind="n")):

                    count = question_answer.questionflowanswer_set.filter(Q(question=qf_question) & Q(void_ind="n")).count()

                    response[f"ans{qf_question.question_id}"] = count + response.get(f"ans{qf_question.question_id}", 0)

        # get aggregates
        question_aggregates = QuestionAggregate.objects.filter(
            Q(void_ind="n") & Q(active="y") & Q(questions__form_typ="field")
        ).distinct()

        for question_aggregate in question_aggregates:
            summation = 0
            for question in question_aggregate.questions.filter(Q(void_ind="n") & Q(active="y")):
                for question_answer in question.questionanswer_set.filter(
                    Q(void_ind="n") & Q(response=scout_field.response)
                ):
                    if question_answer.answer is not None and question_answer.answer != "!EXIST":
                        summation += int(question_answer.answer)
            response[f"ans_sqa{question_aggregate.question_aggregate_id}"] = summation

        response["match"] = scout_field.match.match_number if scout_field.match else None
        response["user"] = scout_field.user.first_name + " " + scout_field.user.last_name
        response["time"] = scout_field.time
        response["user_id"] = scout_field.user.id
        response["team_no"] = scout_field.team_no_id
        response["scout_field_id"] = scout_field.scout_field_id

        try:
            eti = EventTeamInfo.objects.get(
                Q(event=current_event) & Q(team_no=scout_field.team_no) & Q(void_ind="n")
            )
            response["rank"] = eti.rank
        except EventTeamInfo.DoesNotExist:
            response["rank"] = ""

        field_scouting_responses.append(response)

    return {
        "scoutCols": table_cols,
        "scoutAnswers": field_scouting_responses,
        "current_season": current_season,
        "current_event": current_event,
        "removed_responses": get_removed_responses(after_date_time),
    }


def get_removed_responses(before_date_time):
    timeCondition = Q()

    if before_date_time is not None:
        timeCondition = Q(time__lte=before_date_time)

    removed = FieldResponse.objects.filter(
        timeCondition & (Q(void_ind="y") | Q(response__void_ind="y"))
    )

    return removed


def check_in_scout(sfs: FieldSchedule, user_id: int):
    check_in = False
    if sfs.red_one and not sfs.red_one_check_in and sfs.red_one.id == user_id:
        sfs.red_one_check_in = timezone.now()
        check_in = True
    elif sfs.red_two and not sfs.red_two_check_in and sfs.red_two.id == user_id:
        sfs.red_two_check_in = timezone.now()
        check_in = True
    elif sfs.red_three and not sfs.red_three_check_in and sfs.red_three.id == user_id:
        sfs.red_three_check_in = timezone.now()
        check_in = True
    elif sfs.blue_one and not sfs.blue_one_check_in and sfs.blue_one.id == user_id:
        sfs.blue_one_check_in = timezone.now()
        check_in = True
    elif sfs.blue_two and not sfs.blue_two_check_in and sfs.blue_two.id == user_id:
        sfs.blue_two_check_in = timezone.now()
        check_in = True
    elif (
        sfs.blue_three and not sfs.blue_three_check_in and sfs.blue_three.id == user_id
    ):
        sfs.blue_three_check_in = timezone.now()
        check_in = True

    if check_in:
        sfs.save()
        return "Successfully checked in scout for their shift."
    return ""


def get_field_form():
    field_form = scouting.util.get_field_form()

    form_parsed = {
        "field_form": field_form,
        "form_sub_types": form.util.get_form_questions("field")["form_sub_types"]
    }

    return form_parsed


def get_graph_options(graph_type):
    match graph_type:
        case "bar":
            v = 9

# need % and avg

