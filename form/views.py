from django.http import HttpResponse

from django.db import transaction
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import form.util
from form.serializers import (
    QuestionSerializer,
    SaveResponseSerializer,
    ScoutFieldFormResponseSerializer,
    FormInitializationSerializer,
    ResponseSerializer,
    QuestionAggregateSerializer,
    QuestionAggregateTypeSerializer,
    QuestionConditionSerializer, FlowSerializer, QuestionConditionTypeSerializer,
    FlowConditionSerializer,
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
            questions = form.util.get_questions(
                request.query_params["form_typ"],
                active=request.query_params.get("active", ""),
            )
            serializer = QuestionSerializer(questions, many=True)
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
                        error_message=serializer.errors,
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


class FormEditorView(APIView):
    """
    API endpoint to init form editor
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "form-editor/"

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
                flows = form.util.get_flows(None, request.query_params["form_typ"])
                serializer = FormInitializationSerializer(
                    {
                        "questions": questions,
                        "question_types": question_types,
                        "form_sub_types": form_sub_types,
                        "flows": flows
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
                "An error occurred while initializing form editor.",
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
            error_msg = "An error occurred while saving answers."
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
                    serializer = ScoutFieldFormResponseSerializer(data=request.data)
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
                        return ret_message(
                            error_msg,
                            True,
                            app_url + self.endpoint,
                            request.user.id,
                            error_message=serializer.errors,
                        )
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
                    form.util.save_answers(serializer.validated_data)
                else:
                    return ret_message(
                        error_msg,
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        error_message=serializer.errors,
                    )
            return ret_message(success_msg)
        except Exception as e:
            return ret_message(
                error_msg,
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ResponseView(APIView):
    """
    API endpoint to get a form response
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    endpoint = "response/"

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
                "An error occurred while getting the response.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def post(self, request, format=None):
        serializer = ResponseSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                error_message=serializer.errors,
            )

        if has_access(request.user.id, "admin"):
            try:
                with transaction.atomic():
                    form.util.save_response(serializer.validated_data)
                    return ret_message("Saved response successfully")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the response.",
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

    def delete(self, request, format=None):
        try:
            if has_access(request.user.id, "admin"):
                form.util.delete_response(request.query_params["response_id"])
                return ret_message("Successfully deleted the response.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred deleting the response.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class ResponsesView(APIView):
    """
    API endpoint to get a form responses
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    endpoint = "responses/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, "admin"):
                responses = form.util.get_responses(
                    request.query_params["form_typ"],
                    request.query_params.get("archive_ind", "n"),
                )
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
                    error_message=serializer.errors,
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
                    error_message=serializer.errors,
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


class QuestionConditionTypesView(APIView):
    """
    API endpoint to manage the question condition typess
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "question-condition-types/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                qas = form.util.get_question_condition_types()
                serializer = QuestionConditionTypeSerializer(qas, many=True)
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
                "An error occurred while getting question condition types.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class FlowView(APIView):
    """
    API endpoint to get question flows
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "flow/"

    def get(self, request, format=None):
        try:
            fid = request.query_params.get("id", None)
            questions = form.util.get_flows(
                fid,
                request.query_params.get("form_typ", None),
                request.query_params.get("form_sub_typ", None)
            )
            if fid is None:
                serializer = FlowSerializer(questions, many=True)
            else:
                serializer = FlowSerializer(questions[0])
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting question flows.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )

    def post(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                serializer = FlowSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        error_message=serializer.errors,
                    )

                with transaction.atomic():
                    form.util.save_flow(serializer.validated_data)

                return ret_message("Saved flow successfully.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the flow.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class QuestionFlowView(APIView):
    """
    API endpoint to get question flows
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "question-flow/"

    def get(self, request, format=None):
        try:
            fid = request.query_params.get("id", None)
            questions = form.util.get_flows(
                fid,
                request.query_params.get("form_typ", None),
                request.query_params.get("form_sub_typ", None)
            )
            if fid is None:
                serializer = FlowSerializer(questions, many=True)
            else:
                serializer = FlowSerializer(questions[0])
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting question flows.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )

    def post(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                serializer = FlowSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        error_message=serializer.errors,
                    )

                with transaction.atomic():
                    form.util.save_flow(serializer.validated_data)

                return ret_message("Saved question flow successfully.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the question flow.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class FlowConditionView(APIView):
    """
    API endpoint to manage the question conditions
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "flow-condition/"

    def get(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                qas = form.util.get_flow_condition(request.query_params["form_typ"])
                serializer = FlowConditionSerializer(qas, many=True)
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
                "An error occurred while getting flow conditions.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def post(self, request, format=None):
        try:
            serializer = FlowConditionSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                with transaction.atomic():
                    form.util.save_flow_condition(serializer.validated_data)
                return ret_message("Saved flow condition successfully")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the flow condition.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class GraphEditorView(APIView):
    """
    API endpoint to edit graphs
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "graph-editor/"

    def get(self, request, format=None):
        try:
            fid = request.query_params.get("id", None)
            questions = form.util.get_flows(
                fid,
                request.query_params.get("form_typ", None),
                request.query_params.get("form_sub_typ", None)
            )
            if fid is None:
                serializer = FlowSerializer(questions, many=True)
            else:
                serializer = FlowSerializer(questions[0])
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting question flows.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )

    def post(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                serializer = FlowSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        error_message=serializer.errors,
                    )

                with transaction.atomic():
                    form.util.save_flow(serializer.validated_data)

                return ret_message("Saved flow successfully.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving the flow.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )


class GraphView(APIView):
    """
    API endpoint to manage graphs
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "graph/"

    """
    def get(self, request, format=None):
        try:
            fid = request.query_params.get("id", None)
            questions = form.util.get_flows(
                fid,
                request.query_params.get("form_typ", None),
                request.query_params.get("form_sub_typ", None)
            )
            if fid is None:
                serializer = FlowSerializer(questions, many=True)
            else:
                serializer = FlowSerializer(questions[0])
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting question flows.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )
    """

    def post(self, request, format=None):
        try:
            if has_access(request.user.id, "admin") or has_access(
                request.user.id, "scoutadmin"
            ):
                serializer = FlowSerializer(data=request.data)
                if not serializer.is_valid():
                    return ret_message(
                        "Invalid data",
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        error_message=serializer.errors,
                    )

                with transaction.atomic():
                    form.util.save_flow(serializer.validated_data)

                return ret_message("Saved flow successfully.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred while saving graph.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )