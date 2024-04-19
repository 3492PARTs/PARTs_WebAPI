from django.db.models import Q
from django.conf import settings

from form.models import QuestionAggregate, QuestionAnswer
import scouting
import form
from scouting.models import EventTeamInfo, ScoutField


def build_table_columns():
    sqsa = form.util.get_questions_with_conditions("field", "auto")
    sqst = form.util.get_questions_with_conditions("field", "teleop")
    sqso = form.util.get_questions_with_conditions("field", None)

    table_cols = [
        {"PropertyName": "team", "ColLabel": "Team No", "scorable": False, "order": 0},
        {"PropertyName": "rank", "ColLabel": "Rank", "scorable": False, "order": 1},
        {"PropertyName": "match", "ColLabel": "Match", "scorable": False, "order": 1},
    ]

    for sqs in [sqsa, sqst, sqso]:
        for sq in sqs:
            scout_question = scouting.models.Question.objects.get(
                Q(void_ind="n") & Q(question_id=sq["question_id"])
            )
            table_cols.append(
                {
                    "PropertyName": "ans" + str(sq["question_id"]),
                    "ColLabel": (
                        ""
                        if sq.get("form_sub_typ", None) is None
                        else sq["form_sub_typ"][0:1].upper() + ": "
                    )
                    + sq["question"],
                    "scorable": scout_question.scorable,
                    "order": sq["order"],
                }
            )

            for c in sq.get("conditions", []):
                scout_question = scouting.models.Question.objects.get(
                    Q(void_ind="n") & Q(question_id=c["question_to"]["question_id"])
                )
                table_cols.append(
                    {
                        "PropertyName": "ans" + str(c["question_to"]["question_id"]),
                        "ColLabel": (
                            ""
                            if c["question_to"].get("form_sub_typ", None) is None
                            else c["question_to"]["form_sub_typ"][0:1].upper() + ": "
                        )
                        + "C: "
                        + c["condition"]
                        + " "
                        + c["question_to"]["question"],
                        "scorable": scout_question.scorable,
                        "order": c["question_to"]["order"],
                    }
                )

        qas = QuestionAggregate.objects.filter(
            Q(void_ind="n")
            & Q(active="y")
            & Q(questions__question_id__in=set(sq["question_id"] for sq in sqs))
        ).distinct()
        sqas_cnt = 1
        for qa in qas:
            table_cols.append(
                {
                    "PropertyName": "ans_sqa" + str(qa.question_aggregate_id),
                    "ColLabel": (
                        ""
                        if sqs[0].get("form_sub_typ", None) is None
                        else sqs[0]["form_sub_typ"][0:1].upper() + ": "
                    )
                    + qa.field_name,
                    "scorable": True,
                    "order": sqs[len(sqs) - 1]["order"] + sqas_cnt,
                }
            )

            sqas_cnt += 1

    table_cols.append(
        {
            "PropertyName": "user",
            "ColLabel": "Scout",
            "scorable": False,
            "order": 9999999999,
        }
    )
    table_cols.append(
        {
            "PropertyName": "time",
            "ColLabel": "Time",
            "scorable": False,
            "order": 99999999999,
        }
    )

    return table_cols


def get_responses(request, team=None, user=None, after_date_time=None):
    table_cols = build_table_columns()

    field_scouting_responses = []

    current_season = scouting.util.get_current_season()

    if current_season is None:
        return scouting.util.get_no_season_ret_message(
            "scouting.field.util.get_responses", request.user.id
        )

    current_event = scouting.util.get_event(current_season, "y")

    if current_event is None:
        return scouting.util.get_no_season_ret_message(
            "scouting.field.util.get_responses", request.user.id
        )

    # Pull responses by what input
    if team is not None:
        # get response for individual team
        sfs = ScoutField.objects.filter(
            Q(event=current_event) & Q(team_no_id=team) & Q(void_ind="n")
        ).order_by("-time", "-scout_field_id")
    elif user is not None:
        # get response for individual scout
        sfs = ScoutField.objects.filter(
            Q(event=current_event) & Q(user=user) & Q(void_ind="n")
        ).order_by("-time", "-scout_field_id")
    elif after_date_time is not None:
        # get response for individual scout
        sfs = ScoutField.objects.filter(
            Q(event=current_event) & Q(time__gt=after_date_time) & Q(void_ind="n")
        ).order_by("-time", "-scout_field_id")
    else:
        # get responses for all teams
        if settings.DEBUG:
            # don't fetch all responses on local as it's too much
            sfs = ScoutField.objects.filter(
                Q(event=current_event) & Q(void_ind="n")
            ).order_by(
                "-time", "-scout_field_id"
            )  # [:30]
        else:
            # get everything
            sfs = ScoutField.objects.filter(
                Q(event=current_event) & Q(void_ind="n")
            ).order_by("-time", "-scout_field_id")

    # Loop over all the responses selected and put in table
    for sf in sfs:
        qas = QuestionAnswer.objects.filter(Q(response=sf.response) & Q(void_ind="n"))

        response = {}
        for qa in qas:
            response["ans" + str(qa.question_id)] = qa.answer

        # get aggregates
        qas = QuestionAggregate.objects.filter(
            Q(void_ind="n") & Q(active="y") & Q(questions__form_typ="field")
        ).distinct()

        for qa in qas:
            sum = 0
            for q in qa.questions.filter(Q(void_ind="n") & Q(active="y")):
                for a in q.questionanswer_set.filter(
                    Q(void_ind="n") & Q(response=sf.response)
                ):
                    if a.answer is not None and a.answer != "!EXIST":
                        sum += int(a.answer)
            response["ans_sqa" + str(qa.question_aggregate_id)] = sum

        response["match"] = sf.match.match_number if sf.match else None
        response["user"] = sf.user.first_name + " " + sf.user.last_name
        response["time"] = sf.time
        response["user_id"] = sf.user.id
        response["team"] = sf.team_no_id
        response["scout_field_id"] = sf.scout_field_id

        try:
            eti = EventTeamInfo.objects.get(
                Q(event=current_event) & Q(team_no=sf.team_no) & Q(void_ind="n")
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

    removed = ScoutField.objects.filter(
        timeCondition & (Q(void_ind="y") | Q(response__void_ind="y"))
    )

    return removed
