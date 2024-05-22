from django.http import HttpResponse

from django.db import transaction
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import form.util
from form.serializers import (
    QuestionSerializer,
    QuestionWithConditionsSerializer,
    SaveResponseSerializer,
    SaveScoutSerializer,
    QuestionInitializationSerializer,
    ResponseSerializer,
    QuestionAggregateSerializer,
    QuestionAggregateTypeSerializer,
    QuestionConditionSerializer,
)
from general.security import has_access, ret_message

app_url = "form/"


class QuestionView(APIView):
    """
    API endpoint to get questions
    """

    endpoint = "questions/"

    def get(self, request, format=None):
        try:
            questions = form.util.get_questions_with_conditions(
                request.query_params["form_typ"],
                active=request.query_params.get("active", ""),
            )
            serializer = QuestionWithConditionsSerializer(questions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting questions.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )

    def post(self, request, format=None):
        try:
            if request.user.id is None:
                return HttpResponse("Unauthorized", status=401)

            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                serializer = QuestionSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        serializer.errors,
                    )

                with transaction.atomic():
                    form.util.save_question(serializer.validated_data)

                return ret_message("Saved question successfully.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the question.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class FormInitView(APIView):
    """
    API endpoint to init form editor
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "form-init/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):

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

            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while initializing form.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class SaveAnswersView(APIView):
    """
    API endpoint to save answers
    """

    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = "save-answers/"

    def post(self, request, format=None):
        try:
            success_msg = "Response saved successfully."
            form_typ = request.data.get("form_typ", "")
            # with transaction.atomic():
            if form_typ in ["field", "pit"]:
                # field and pit responses must be authenticated
                # Without a user id report unauthenticated
                if request.user.id is None:
                    return HttpResponse("Unauthorized", status=401)

                if (
                    form_typ == "field" and has_access(request.user.id, "scoutfield")
                ) or (form_typ == "pit" and has_access(request.user.id, "scoutpit")):
                    # Try to deserialize as a field or pit answer
                    serializer = SaveScoutSerializer(data=request.data)
                    if serializer.is_valid():
                        if serializer.validated_data["form_typ"] == "field":
                            form.util.save_field_response(
                                serializer.validated_data, request.user.id
                            )
                            success_msg = "Field response saved successfully."
                        else:
                            form.util.save_pit_response(
                                serializer.validated_data, request.user.id
                            )
                            success_msg = "Pit response saved successfully."
                    else:
                        # Serializer is not valid
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
                    form.util.save_response(serializer.validated_data)
                else:
                    raise Exception("Invalid Data")
            return ret_message(success_msg)
        except Exception as e:
            return ret_message(
                "An error occurred while saving answers.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ResponseView(APIView):
    """
    API endpoint to get a form response
    """

    endpoint = "get-response/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, "admin"):
                response = form.util.get_response(request.query_params["response_id"])
                serializer = QuestionSerializer(response, many=True)
                return Response(serializer.data)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while getting responses.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ResponsesView(APIView):
    """
    API endpoint to get a form responses
    """

    endpoint = "get-responses/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, "admin"):
                responses = form.util.get_responses(request.query_params["form_typ"])
                serializer = ResponseSerializer(responses, many=True)
                return Response(serializer.data)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while getting responses.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class QuestionAggregateView(APIView):
    """
    API endpoint to manage the question aggregate groups
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "question-aggregate/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                qas = form.util.get_question_aggregates(
                    request.query_params["form_typ"]
                )
                serializer = QuestionAggregateSerializer(qas, many=True)
                return Response(serializer.data)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while getting question aggregates.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def post(self, request, format=None):
        try:
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
                with transaction.atomic():
                    form.util.save_question_aggregate(serializer.validated_data)
                return ret_message("Saved question aggregate successfully")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the question aggregate.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
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
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                qas = form.util.get_question_condition(request.query_params["form_typ"])
                serializer = QuestionConditionSerializer(qas, many=True)
                return Response(serializer.data)
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while getting question conditions.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def post(self, request, format=None):
        try:
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
                with transaction.atomic():
                    form.util.save_question_condition(serializer.validated_data)
                return ret_message("Saved question condition successfully")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the question condition.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )
