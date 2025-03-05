from django.db.models import Q, Exists, OuterRef
from django.conf import settings
from django.utils import timezone
import datetime

from form.models import (
    QuestionAggregate,
    Answer,
    FormSubType,
    FlowAnswer,
    QuestionAggregateQuestion,
)
import form.urls
import scouting.models
import scouting.util
import form
from scouting.models import EventTeamInfo, FieldResponse, FieldSchedule
import general.util
import form.util


def build_table_columns(question_aggregates):
    # sqsa = form.util.get_form_questions("field", "auto")
    # sqst = form.util.get_form_questions("field", "teleop")
    # sqso = form.util.get_form_questions("field", "post")

    form_questions = form.util.get_form_questions("field")

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
            table_cols.append(
                {
                    "PropertyName": "ans" + str(question["id"]),
                    "ColLabel": (
                        ""
                        if question.get("form_sub_typ", None) is None
                        else question.get("form_sub_typ").form_sub_typ[0:1].upper()
                        + ": "
                    )
                    + (" C: " if len(question["conditional_on_questions"]) > 0 else "")
                    + question["question"],
                    "Width": question["table_col_width"],
                    "order": question["order"],
                }
            )

        for flow in form_sub_type["flows"]:
            for question_flow in flow["flow_questions"]:
                property_name = f"ans{question_flow['question']['id']}"

                try:
                    [tc for tc in table_cols if tc["PropertyName"] == property_name][0]
                except IndexError:
                    table_cols.append(
                        {
                            "PropertyName": property_name,
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
                            + " F: "
                            + question_flow["question"]["question"],
                            "Width": question_flow["question"]["table_col_width"],
                            "order": question_flow["question"]["order"],
                        }
                    )

    question_aggregate_count = 1
    for question_aggregate in question_aggregates:
        table_cols.append(
            {
                "PropertyName": f"ans_sqa{question_aggregate.id}",
                "ColLabel": f"AGG: {question_aggregate.name}",
                "Width": "100px",
                "order": len(table_cols) + 1,
            }
        )

        question_aggregate_count += 1

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

    current_season = scouting.util.get_current_season()

    current_event = scouting.util.get_current_event()

    # get aggregates
    question_aggregates = QuestionAggregate.objects.filter(
        Q(void_ind="n")
        & Q(active="y")
        & Q(horizontal=True)
        & Exists(
            QuestionAggregateQuestion.objects.filter(
                Q(question_aggregate_id=OuterRef("pk"))
                & Q(active="y")
                & Q(void_ind="n")
                & Q(question__form_typ_id="field")
                & Q(question__active="y")
                & Q(question__void_ind="n")
                & Exists(
                    scouting.models.Question.objects.filter(
                        Q(question_id=OuterRef("question_id"))
                        & Q(season=current_season)
                        & Q(void_ind="n")
                    )
                )
            )
        )
    )

    table_cols = build_table_columns(question_aggregates)

    field_scouting_responses = []

    if current_event is None:
        return scouting.util.get_no_event_ret_message(
            "scouting.field.util.get_responses", request.user.id
        )

    parsed_question_aggregates = []
    for question_aggregate in question_aggregates:
        parsed_question_aggregates.append(
            {
                "parsed_question_aggregate": form.util.parse_question_aggregate(
                    question_aggregate
                ),
                "questions": [
                    form.util.parse_question(question_aggregate_question.question)
                    for question_aggregate_question in question_aggregate.questionaggregatequestion_set.filter(
                        Q(void_ind="n")
                        & Q(active="y")
                        & Q(question__void_ind="n")
                        & Q(question__active="y")
                    )
                ],
            }
        )

    # Pull responses by what input
    if team is not None:
        # get response for individual team
        scout_fields = (
            FieldResponse.objects.prefetch_related("team__eventteaminfo_set")
            .filter(Q(event=current_event) & Q(team_no_id=team) & Q(void_ind="n"))
            .order_by("-time", "-id")
        )
    elif user is not None:
        # get response for individual scout
        scout_fields = (
            FieldResponse.objects.prefetch_related("team__eventteaminfo_set")
            .filter(Q(event=current_event) & Q(user=user) & Q(void_ind="n"))
            .order_by("-time", "-id")
        )
    elif after_scout_field_id is not None:
        # get response for individual scout
        scout_fields = (
            FieldResponse.objects.prefetch_related("team__eventteaminfo_set")
            .filter(
                Q(event=current_event)
                & Q(id__gt=after_scout_field_id)
                & Q(void_ind="n")
            )
            .order_by("-time", "-id")
        )
    else:
        loading_all = True
        # get everything
        scout_fields = (
            FieldResponse.objects.prefetch_related("team__eventteaminfo_set")
            .filter(Q(event=current_event) & Q(void_ind="n"))
            .order_by("-time", "-id")
        )

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

        for parsed_question_aggregate in parsed_question_aggregates:
            response[
                f"ans_sqa{parsed_question_aggregate['parsed_question_aggregate']['id']}"
            ] = form.util.aggregate_answers_horizontally(
                parsed_question_aggregate["parsed_question_aggregate"],
                scout_field.response,
                parsed_question_aggregate["questions"],
            )

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
            eti = scout_field.team.eventteaminfo_set.get(
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
        "removed_responses": [
            field_response.id
            for field_response in (
                get_removed_responses(after_scout_field_id) if not loading_all else []
            )
        ],
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
