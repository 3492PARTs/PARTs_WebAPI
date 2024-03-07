import pytz

from django.db import transaction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import alerts.util
import form.util
import user.util
from form.models import Question, QuestionAnswer, FormType
from form.serializers import (
    QuestionSerializer,
    SaveResponseSerializer,
    SaveScoutSerializer,
    QuestionInitializationSerializer,
    ResponseSerializer,
    QuestionAggregateSerializer,
    QuestionAggregateTypeSerializer,
    QuestionConditionSerializer,
)
from general.security import has_access, ret_message
from scouting.models import Event, Season, ScoutField, ScoutPit, UserInfo, Match

app_url = "form/"


class GetQuestions(APIView):
    """
    API endpoint to init form editor
    """

    endpoint = "get-questions/"

    def get(self, request, format=None):
        try:
            questions = form.util.get_questions(
                request.query_params["form_typ"], request.query_params.get("active", "")
            )
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting questions.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class GetFormInit(APIView):
    """
    API endpoint to init form editor
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "form-init/"

    def get(self, request, format=None):
        if has_access(request.user.id, "admin") or has_access(
            request.user.id, "scoutadmin"
        ):
            try:
                questions = form.util.get_questions(request.query_params["form_typ"])
                question_types = form.util.get_question_types()
                form_sub_types = form.util.get_form_sub_types(
                    request.query_params["form_typ"]
                )
                serializer = QuestionInitializationSerializer(
                    {
                        "questions": questions,
                        "question_types": question_types,
                        "form_sub_types": form_sub_types,
                    }
                )
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


class SaveQuestion(APIView):
    """API endpoint to save new questions"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "save-question/"

    def post(self, request, format=None):
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, "admin") or has_access(
            request.user.id, "scoutadmin"
        ):
            try:
                with transaction.atomic():
                    form.util.save_question(serializer.validated_data)
                return ret_message("Saved question successfully.")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the question.",
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


class SaveAnswers(APIView):
    """
    API endpoint to save answers
    """

    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = "save-answers/"

    def post(self, request, format=None):
        success_msg = "Response saved successfully"
        form_typ = request.data.get("form_typ", "")
        with transaction.atomic():
            try:
                if form_typ in ["field", "pit"]:
                    # field and pit responses must be authenticated
                    if (
                        form_typ == "field"
                        and has_access(request.user.id, "scoutfield")
                    ) or (
                        form_typ == "pit" and has_access(request.user.id, "scoutpit")
                    ):
                        try:
                            current_event = Event.objects.get(
                                Q(season=Season.objects.get(current="y"))
                                & Q(current="y")
                            )
                        except Exception as e:
                            raise Exception("No event set, see an admin")

                        # Try to deserialize as a field or pit answer
                        serializer = SaveScoutSerializer(data=request.data)
                        if serializer.is_valid():
                            form_type = FormType.objects.get(
                                form_typ=serializer.validated_data["form_typ"]
                            )
                            try:
                                r = form.models.Response.objects.get(
                                    response_id=serializer.validated_data.get(
                                        "response_id", None
                                    )
                                )
                            except form.models.Response.DoesNotExist:
                                r = form.models.Response(form_typ=form_type)
                                r.save()

                            if serializer.validated_data["form_typ"] == "field":
                                try:
                                    m = Match.objects.get(
                                        match_id=serializer.validated_data.get(
                                            "match", None
                                        )
                                    )
                                except Match.DoesNotExist:
                                    m = None

                                sf = ScoutField(
                                    event=current_event,
                                    team_no_id=serializer.validated_data["team"],
                                    match=m,
                                    user_id=request.user.id,
                                    response_id=r.response_id,
                                    void_ind="n",
                                )
                                sf.save()

                                # Check if previous match is missing any results
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
                            else:
                                try:
                                    sp = ScoutPit.objects.get(
                                        Q(team_no_id=serializer.data["team"])
                                        & Q(void_ind="n")
                                        & Q(event=current_event)
                                        & Q(response=r)
                                    )
                                except ScoutPit.DoesNotExist:
                                    sp = ScoutPit(
                                        event=current_event,
                                        team_no_id=serializer.data["team"],
                                        user_id=request.user.id,
                                        response_id=r.response_id,
                                        void_ind="n",
                                    )
                                    sp.save()
                        else:
                            raise Exception("Invalid Data")
                    else:
                        return ret_message(
                            "You do not have access.",
                            True,
                            app_url + self.endpoint,
                            request.user.id,
                        )
                else:
                    # regular response
                    serializer = SaveResponseSerializer(data=request.data)
                    if serializer.is_valid():
                        form_type = FormType.objects.get(
                            form_typ=serializer.validated_data["form_typ"]
                        )
                        r = form.models.Response(form_typ=form_type)
                        r.save()

                        alert = []
                        users = user.util.get_users_with_permission("site_forms_notif")
                        for u in users:
                            alert.append(
                                alerts.util.stage_alert(
                                    u,
                                    form_type.form_nm,
                                    "A new response has been logged.",
                                )
                            )
                        for a in alert:
                            for acct in ["email", "message", "notification"]:
                                alerts.util.stage_alert_channel_send(a, acct)
                    else:
                        raise Exception("Invalid Data")

                for d in serializer.validated_data.get("question_answers", []):
                    try:
                        spa = QuestionAnswer.objects.get(
                            Q(response=r)
                            & Q(question_id=d.get("question_id", None))
                            & Q(void_ind="n")
                        )
                        spa.answer = d.get("answer", "")
                        spa.save()
                    except QuestionAnswer.DoesNotExist:
                        form.util.save_question_answer(
                            d.get("answer", ""),
                            Question.objects.get(question_id=d["question_id"]),
                            r,
                        )

                    for c in d.get("conditions", []):
                        try:
                            spa = QuestionAnswer.objects.get(
                                Q(response=r)
                                & Q(question_id=c["question_to"]["question_id"])
                                & Q(void_ind="n")
                            )
                            spa.answer = c["question_to"].get("answer", "")
                            spa.save()
                        except QuestionAnswer.DoesNotExist:
                            form.util.save_question_answer(
                                c["question_to"].get("answer", ""),
                                Question.objects.get(
                                    question_id=c["question_to"]["question_id"]
                                ),
                                r,
                            )

                return ret_message(success_msg)
            except Exception as e:
                return ret_message(
                    "An error occurred while saving answers.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )


class GetResponse(APIView):
    """
    API endpoint to get a form response
    """

    endpoint = "get-response/"

    def get(self, request, format=None):
        if has_access(request.user.id, "admin"):
            try:
                response = form.util.get_response(request.query_params["response_id"])
                serializer = QuestionSerializer(response, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting responses.",
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


class GetResponses(APIView):
    """
    API endpoint to get a form responses
    """

    endpoint = "get-responses/"

    def get(self, request, format=None):
        if has_access(request.user.id, "admin"):
            try:
                responses = form.util.get_responses(request.query_params["form_typ"])
                serializer = ResponseSerializer(responses, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting responses.",
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


class QuestionAggregateView(APIView):
    """
    API endpoint to manage the question aggregate groups
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "question-aggregate/"

    def get(self, request, format=None):
        if has_access(request.user.id, "admin") or has_access(
            request.user.id, "scoutadmin"
        ):
            try:
                qas = form.util.get_question_aggregates(
                    request.query_params["form_typ"]
                )
                serializer = QuestionAggregateSerializer(qas, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting question aggregates.",
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

    def post(self, request, format=None):
        serializer = QuestionAggregateSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, "admin") or has_access(
            request.user.id, "scoutadmin"
        ):
            try:
                with transaction.atomic():
                    form.util.save_question_aggregate(serializer.validated_data)
                return ret_message("Saved question aggregate successfully")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the question aggregate.",
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


class QuestionAggregateTypeView(APIView):
    """
    API endpoint to manage the question aggregate types
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "question-aggregate-types/"

    def get(self, request, format=None):
        try:
            qas = form.util.get_question_aggregate_types()
            serializer = QuestionAggregateTypeSerializer(qas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting question aggregate types.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class QuestionConditionView(APIView):
    """
    API endpoint to manage the question conditions
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "question-condition/"

    def get(self, request, format=None):
        if has_access(request.user.id, "admin") or has_access(
            request.user.id, "scoutadmin"
        ):
            try:
                qas = form.util.get_question_condition(request.query_params["form_typ"])
                serializer = QuestionConditionSerializer(qas, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting question conditions.",
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

    def post(self, request, format=None):
        serializer = QuestionConditionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                serializer.errors,
            )

        if has_access(request.user.id, "admin") or has_access(
            request.user.id, "scoutadmin"
        ):
            try:
                with transaction.atomic():
                    form.util.save_question_condition(serializer.validated_data)
                return ret_message("Saved question condition successfully")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the question condition.",
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
