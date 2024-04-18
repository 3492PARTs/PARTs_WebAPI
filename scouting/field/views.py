from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import form.util
import scouting.util
import scouting.models
from form.models import QuestionAnswer, QuestionAggregate
from scouting.models import (
    Season,
    Event,
    Team,
    ScoutFieldSchedule,
    ScoutField,
    EventTeamInfo,
    Match,
)
from rest_framework.views import APIView
from general.security import ret_message, has_access
from .serializers import (
    ScoutFieldSerializer,
    ScoutFieldResultsSerializer,
)
from django.db.models import Q
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings

auth_obj = "scoutfield"
auth_view_obj = "scoutFieldResults"
app_url = "scouting/field/"


class Init(APIView):
    """
    API endpoint to get scout field inputs
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "init/"

    def get_questions(self):

        current_season = scouting.util.get_current_season()

        if current_season is None:
            return scouting.util.get_no_season_ret_message(
                app_url + self.endpoint, self.request.user.id
            )

        current_event = scouting.util.get_event(current_season, "y")

        if current_event is None:
            return scouting.util.get_no_season_ret_message(
                app_url + self.endpoint, self.request.user.id
            )

        # scout_questions = form.util.get_questions('field', 'y')
        scout_questions = form.util.get_questions_with_conditions("field")

        sfss = ScoutFieldSchedule.objects.filter(
            Q(st_time__lte=timezone.now())
            & Q(end_time__gte=timezone.now())
            & Q(void_ind="n")
        )

        sfs = None
        for s in sfss:
            sfs = scouting.util.format_scout_field_schedule_entry(s)

        matches = Match.objects.filter(
            Q(event=current_event) & Q(comp_level_id="qm") & Q(void_ind="n")
        ).order_by("match_number")
        parsed_matches = []

        for m in matches:
            blue_one_id = (
                m.blue_one.team_no
                if self.get_team_match_field_result(m, m.blue_one.team_no) is None
                else None
            )
            blue_two_id = (
                m.blue_two.team_no
                if self.get_team_match_field_result(m, m.blue_two.team_no) is None
                else None
            )
            blue_three_id = (
                m.blue_three.team_no
                if self.get_team_match_field_result(m, m.blue_three.team_no) is None
                else None
            )
            red_one_id = (
                m.red_one.team_no
                if self.get_team_match_field_result(m, m.red_one.team_no) is None
                else None
            )
            red_two_id = (
                m.red_two.team_no
                if self.get_team_match_field_result(m, m.red_two.team_no) is None
                else None
            )
            red_three_id = (
                m.red_three.team_no
                if self.get_team_match_field_result(m, m.red_three.team_no) is None
                else None
            )

            if (
                blue_one_id is not None
                or blue_two_id is not None
                or blue_three_id is not None
                or red_one_id is not None
                or red_two_id is not None
                or red_three_id is not None
            ):
                parsed_matches.append(
                    {
                        "match_id": m.match_id,
                        "event_id": m.event.event_id,
                        "match_number": m.match_number,
                        "time": m.time,
                        "blue_one": blue_one_id,
                        "blue_two": blue_two_id,
                        "blue_three": blue_three_id,
                        "red_one": red_one_id,
                        "red_two": red_two_id,
                        "red_three": red_three_id,
                    }
                )

        return {
            "scoutQuestions": scout_questions,
            "scoutFieldSchedule": sfs,
            "matches": parsed_matches,
        }

    def get_team_match_field_result(self, m, team):
        res = ScoutField.objects.filter(Q(match=m) & Q(team_no=team) & Q(void_ind="n"))
        if res.count() > 0:
            return res
        else:
            return None

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions()

                if type(req) == Response:
                    return req

                serializer = ScoutFieldSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while initializing.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class Results(APIView):
    """
    API endpoint to get the results of field scouting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "results/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj) or has_access(
            request.user.id, auth_view_obj
        ):
            try:
                req = get_field_results(
                    request.query_params.get("team", None), self.endpoint, self.request
                )

                if type(req) == Response:
                    return req

                serializer = ScoutFieldResultsSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while initializing.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


def get_field_results(team, endpoint, request, user=None):
    current_season = scouting.util.get_current_season()

    if current_season is None:
        return scouting.util.get_no_season_ret_message(
            app_url + endpoint, request.user.id
        )

    current_event = scouting.util.get_event(current_season, "y")

    if current_event is None:
        return scouting.util.get_no_season_ret_message(
            app_url + endpoint, request.user.id
        )

    table_cols = [
        {"PropertyName": "team", "ColLabel": "Team No", "scorable": False, "order": 0},
        {"PropertyName": "rank", "ColLabel": "Rank", "scorable": False, "order": 1},
        {"PropertyName": "match", "ColLabel": "Match", "scorable": False, "order": 1},
    ]

    field_scouting_responses = []

    sqsa = form.util.get_questions_with_conditions("field", "auto")
    sqst = form.util.get_questions_with_conditions("field", "teleop")
    sqso = form.util.get_questions_with_conditions("field", None)

    # Build table columns ------------------------------------
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
    # End Build table columns ------------------------------------

    # Responses to fetch
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
    else:
        # get responses for all teams
        if settings.DEBUG:
            # don't fetch all responses on local as it's too much
            sfs = ScoutField.objects.filter(
                Q(event=current_event) & Q(void_ind="n")
            ).order_by("-time", "-scout_field_id")[:30]
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

    return {"scoutCols": table_cols, "scoutAnswers": field_scouting_responses}


class CheckIn(APIView):
    """
    API endpoint to let a field scout check in for thier shift
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "check-in/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                sfs = ScoutFieldSchedule.objects.get(
                    scout_field_sch_id=request.query_params.get(
                        "scout_field_sch_id", None
                    )
                )

                return ret_message(check_in_scout(sfs, request.user.id))
            except Exception as e:
                return ret_message(
                    "An error occurred while checking in the scout for their shift.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


def check_in_scout(sfs: ScoutFieldSchedule, user_id: int):
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
