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
    QuestionConditionSerializer,
    FlowSerializer,
    QuestionConditionTypeSerializer,
    FlowConditionSerializer,
    GraphEditorSerializer,
    GraphSerializer,
)
from general.security import ret_message, access_response

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
        def fun():
            if request.user.id is None:
                return HttpResponse("Unauthorized", status=401)
            
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

        # Try first permission
        if request.user.id is None:
            return HttpResponse("Unauthorized", status=401)
            
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving the question.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while saving the question.",
                fun,
            )
        return result


class FormEditorView(APIView):
    """
    API endpoint to init form editor
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "form-editor/"

    def get(self, request, format=None):
        def fun():
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
                    "flows": flows,
                }
            )
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while initializing form editor.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while initializing form editor.",
                fun,
            )
        return result


class SaveAnswersView(APIView):
    """
    API endpoint to save answers
    """

    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = "save-answers/"

    def post(self, request, format=None):
        success_msg = "Response saved successfully."
        error_msg = "An error occurred while saving answers."
        form_typ = request.data.get("form_typ", "")
        
        if form_typ in ["field", "pit"]:
            # field and pit responses must be authenticated
            if request.user.id is None:
                return HttpResponse("Unauthorized", status=401)

            def fun():
                # Try to deserialize as a field or pit answer
                serializer = ScoutFieldFormResponseSerializer(data=request.data)
                if serializer.is_valid():
                    if serializer.validated_data["form_typ"] == "field":
                        form.util.save_field_response(
                            serializer.validated_data, request.user.id
                        )
                        return ret_message("Field response saved successfully.")
                    else:
                        form.util.save_pit_response(
                            serializer.validated_data, request.user.id
                        )
                        return ret_message("Pit response saved successfully.")
                else:
                    # Serializer is not valid
                    return ret_message(
                        error_msg,
                        True,
                        app_url + self.endpoint,
                        request.user.id,
                        error_message=serializer.errors,
                    )

            permission = "scoutfield" if form_typ == "field" else "scoutpit"
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                permission,
                error_msg,
                fun,
            )
        else:
            # regular response - no auth required
            try:
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
        def fun():
            response = form.util.get_response(request.query_params["response_id"])
            serializer = QuestionSerializer(response, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while getting the response.",
            fun,
        )

    def post(self, request, format=None):
        def fun():
            serializer = ResponseSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )
            with transaction.atomic():
                form.util.save_response(serializer.validated_data)
                return ret_message("Saved response successfully")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving the response.",
            fun,
        )

    def delete(self, request, format=None):
        def fun():
            form.util.delete_response(request.query_params["response_id"])
            return ret_message("Successfully deleted the response.")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred deleting the response.",
            fun,
        )
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
        def fun():
            responses = form.util.get_responses(
                request.query_params["form_typ"],
                request.query_params.get("archive_ind", "n"),
            )
            serializer = ResponseSerializer(responses, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while getting responses.",
            fun,
        )


class QuestionAggregateView(APIView):
    """
    API endpoint to manage the question aggregate groups
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "question-aggregate/"

    def get(self, request, format=None):
        def fun():
            qas = form.util.get_question_aggregates(
                request.query_params["form_typ"]
            )
            serializer = QuestionAggregateSerializer(qas, many=True)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while getting question aggregates.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while getting question aggregates.",
                fun,
            )
        return result

    def post(self, request, format=None):
        def fun():
            serializer = QuestionAggregateSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )
            with transaction.atomic():
                form.util.save_question_aggregate(serializer.validated_data)
            return ret_message("Saved question aggregate successfully")

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving the question aggregate.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while saving the question aggregate.",
                fun,
            )
        return result


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
        def fun():
            qas = form.util.get_question_conditions(
                request.query_params["form_typ"]
            )
            serializer = QuestionConditionSerializer(qas, many=True)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while getting question conditions.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while getting question conditions.",
                fun,
            )
        return result

    def post(self, request, format=None):
        def fun():
            serializer = QuestionConditionSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )
            with transaction.atomic():
                form.util.save_question_condition(serializer.validated_data)
            return ret_message("Saved question condition successfully")

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving the question condition.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while saving the question condition.",
                fun,
            )
        return result
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
        def fun():
            qas = form.util.get_question_condition_types()
            serializer = QuestionConditionTypeSerializer(qas, many=True)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while getting question condition types.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while getting question condition types.",
                fun,
            )
        return result


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
                request.query_params.get("form_sub_typ", None),
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
        def fun():
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

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving the flow.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while saving the flow.",
                fun,
            )
        return result


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
                request.query_params.get("form_sub_typ", None),
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
        def fun():
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

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving the question flow.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while saving the question flow.",
                fun,
            )
        return result


class FlowConditionView(APIView):
    """
    API endpoint to manage the question conditions
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "flow-condition/"

    def get(self, request, format=None):
        def fun():
            qas = form.util.get_flow_condition(request.query_params["form_typ"])
            serializer = FlowConditionSerializer(qas, many=True)
            return Response(serializer.data)

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while getting flow conditions.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while getting flow conditions.",
                fun,
            )
        return result

    def post(self, request, format=None):
        def fun():
            serializer = FlowConditionSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )
            with transaction.atomic():
                form.util.save_flow_condition(serializer.validated_data)
            return ret_message("Saved flow condition successfully")

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving the flow condition.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while saving the flow condition.",
                fun,
            )
        return result


class GraphEditorView(APIView):
    """
    API endpoint to edit graphs
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "graph-editor/"

    def get(self, request, format=None):
        try:
            graph_types = form.util.get_graph_types()
            graph_question_types = form.util.get_graph_question_types()
            graphs = form.util.get_graphs(True)
            question_condition_types = form.util.get_question_condition_types()
            serializer = GraphEditorSerializer(
                {
                    "graph_types": graph_types,
                    "graph_question_types": graph_question_types,
                    "graphs": graphs,
                    "question_condition_types": question_condition_types,
                }
            )
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting graph editor.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


class GraphView(APIView):
    """
    API endpoint to manage graphs
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "graph/"

    def get(self, request, format=None):
        try:
            gid = request.query_params.get("graph_id", None)
            graphs = form.util.get_graphs(gid is None, gid)
            if gid is None:
                serializer = GraphSerializer(graphs, many=True)
            else:
                serializer = GraphSerializer(graphs[0])
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting graphs.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )

    def post(self, request, format=None):
        def fun():
            serializer = GraphSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            form.util.save_graph(serializer.validated_data, request.user.id, True)
            return ret_message("Saved graph successfully.")

        # Try first permission
        result = access_response(
            app_url + self.endpoint,
            request.user.id,
            "admin",
            "An error occurred while saving graph.",
            fun,
        )
        # If access denied, try second permission
        if result.data.get("error") and "do not have access" in result.data.get("retMessage", ""):
            return access_response(
                app_url + self.endpoint,
                request.user.id,
                "scoutadmin",
                "An error occurred while saving graph.",
                fun,
            )
        return result
