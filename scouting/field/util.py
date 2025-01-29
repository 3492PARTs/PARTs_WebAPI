from django.db.models import Q
from django.conf import settings
from django.utils import timezone
import datetime

from form.models import QuestionAggregate, Answer, FormSubType, FlowAnswer
import scouting.util
import form
from scouting.models import EventTeamInfo, FieldResponse, FieldSchedule
import general.util
import form.util


def build_table_columns():
    # sqsa = form.util.get_form_questions("field", "auto")
    # sqst = form.util.get_form_questions("field", "teleop")
    # sqso = form.util.get_form_questions("field", "post")

    form_questions = form.util.get_form_questions("field")
    all_questions = []

    table_cols = [
        {
            "PropertyName": "team_id",
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
                    "PropertyName": "ans" + str(question["id"]),
                    "ColLabel": (
                        ""
                        if question.get("form_sub_typ", None) is None
                        else question.get("form_sub_typ").form_sub_typ[0:1].upper()
                        + ": "
                    )
                    + (
                        " C: "
                        if question["question_conditional_on"] is not None
                        else ""
                    )
                    + question["question"],
                    "Width": question["table_col_width"],
                    "order": question["order"],
                }
            )

        for flow in form_sub_type["question_flows"]:
            for question_flow in flow["questions"]:
                all_questions.append(question_flow["question"])
                table_cols.append(
                    {
                        "PropertyName": "ans" + str(question_flow["question"]["id"]),
                        "ColLabel": (
                            ""
                            if question_flow["question"].get("form_sub_typ", None)
                            is None
                            else question_flow["question"]
                            .get("form_sub_typ")
                            .form_sub_typ[0:1]
                            .upper()
                            + ": "
                        )
                        + " QF: "
                        + question_flow["question"]["question"],
                        "Width": question_flow["question"]["table_col_width"],
                        "order": question_flow["question"]["order"],
                    }
                )

        question_aggregates = QuestionAggregate.objects.filter(
            Q(void_ind="n")
            & Q(active="y")
            & Q(questions__id__in=set(q["id"] for q in all_questions))
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


def get_responses(request, team=None, user=None, after_scout_field_id=None):
    loading_all = False

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
        ).order_by("-time", "-id")
    elif user is not None:
        # get response for individual scout
        scout_fields = FieldResponse.objects.filter(
            Q(event=current_event) & Q(user=user) & Q(void_ind="n")
        ).order_by("-time", "-id")
    elif after_scout_field_id is not None:
        # get response for individual scout
        scout_fields = FieldResponse.objects.filter(
            Q(event=current_event) & Q(id__gt=after_scout_field_id) & Q(void_ind="n")
        ).order_by("-time", "-id")
    else:
        loading_all = True
        # get everything
        scout_fields = FieldResponse.objects.filter(
            Q(event=current_event) & Q(void_ind="n")
        ).order_by("-time", "-id")

    # Loop over all the responses selected and put in table
    for scout_field in scout_fields:
        answers = Answer.objects.filter(
            Q(response=scout_field.response) & Q(void_ind="n")
        )

        response = {}
        for answer in answers:
            if answer.question is not None:
                response[f"ans{answer.question.id}"] = answer.value
            if answer.flow is not None:
                for flow_answer in answer.flowanswer_set.filter(void_ind="n"):
                    response[f"ans{flow_answer.question.id}"] = 1 + response.get(
                        f"ans{flow_answer.question.id}", 0
                    )

        # get aggregates
        question_aggregates = QuestionAggregate.objects.filter(
            Q(void_ind="n") & Q(active="y") & Q(questions__form_typ="field")
        ).distinct()

        for question_aggregate in question_aggregates:
            summation = 0
            for question in question_aggregate.questions.filter(
                Q(void_ind="n") & Q(active="y")
            ):
                for answer in question.questionanswer_set.filter(
                    Q(void_ind="n") & Q(response=scout_field.response)
                ):
                    if answer.value is not None and answer.value != "!EXIST":
                        summation += int(answer.value)
            response[f"ans_sqa{question_aggregate.question_aggregate_id}"] = summation

        response["match"] = (
            scout_field.match.match_number if scout_field.match else None
        )
        response["user"] = (
            scout_field.user.first_name + " " + scout_field.user.last_name
        )
        response["time"] = scout_field.time
        response["user_id"] = scout_field.user.id
        response["team_id"] = scout_field.team_id
        response["id"] = scout_field.id

        try:
            eti = EventTeamInfo.objects.get(
                Q(event=current_event) & Q(team=scout_field.team) & Q(void_ind="n")
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
        "removed_responses": [field_response.id for field_response in
                              (get_removed_responses(after_scout_field_id) if not loading_all else [])]
        ,
    }


def get_removed_responses(before_scout_field_id=None):
    condition = Q()

    if before_scout_field_id is not None:
        condition = Q(id__lte=before_scout_field_id)

    removed = FieldResponse.objects.filter(
        condition & (Q(void_ind="y") | Q(response__void_ind="y"))
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
        "form_sub_types": form.util.get_form_questions("field")["form_sub_types"],
    }

    return form_parsed


def get_graph_options(graph_type):
    match graph_type:
        case "bar":
            v = 9


# need % and avg


def get_scouting_responses():
    parsed_responses = []
    event = scouting.util.get_current_event()

    responses = FieldResponse.objects.filter(Q(event=event) & Q(void_ind="n")).order_by(
        "-time"
    )

    for response in responses[:10]:
        parsed_answers = form.util.get_response_answers(response.response)

        parsed_responses.append(
            {
                "id": response.id,
                "match": (
                    scouting.util.parse_match(response.match)
                    if response.match is not None
                    else None
                ),
                "user": response.user,
                "time": response.time,
                "answers": parsed_answers,
                "display_value": f"{'Match: ' + str(response.match.match_number) + ' ' if response.match is not None else ''}Team: {response.team.team_no} {response.user.get_full_name()} {general.util.date_time_to_mdyhm(response.time, event.timezone)}",
            }
        )

    return parsed_responses
