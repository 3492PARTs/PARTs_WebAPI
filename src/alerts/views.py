from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import alerts.util_alert_definitions
import alerts.util
from general.security import access_response, ret_message
from alerts.serializers import AlertTypeSerializer
from admin.views import auth_obj as auth_obj_admin

app_url = "alerts/"


class StageAlertsView(APIView):
    """
    API endpoint to stage user alerts.
    
    This view triggers the staging of alerts defined in alert definitions.
    """

    endpoint = "stage/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to stage all alerts.
        
        Returns:
            Response with success message or error message
        """
        try:
            ret = "STAGE ALERTS: "
            ret += alerts.util_alert_definitions.stage_alerts()
            return ret_message(ret)
        except Exception as e:
            return ret_message(
                "An error occurred while staging alerts.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


class SendAlertsView(APIView):
    """
    API endpoint to send queued alerts to users.
    
    This view processes staged alerts and sends them through configured channels.
    """

    endpoint = "send/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to send all staged alerts.
        
        Returns:
            Response with success message or error message
        """
        try:
            ret = "SEND ALERTS: "
            ret += alerts.util.send_alerts()
            return ret_message(ret)
        except Exception as e:
            return ret_message(
                "An error occurred while sending alerts.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


class RunAlertsView(APIView):
    """
    API endpoint to stage and send alerts in one operation.
    
    This view combines staging and sending of alerts for convenience.
    """

    endpoint = "run/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to stage and send all alerts.
        
        Returns:
            Response with success message or error message
        """
        try:
            ret = "RUN ALERTS: "
            ret += "STAGE ALERTS: "
            ret += alerts.util_alert_definitions.stage_alerts()
            ret += "SEND ALERTS: "
            ret += alerts.util.send_alerts()
            return ret_message(ret)
        except Exception as e:
            return ret_message(
                "An error occurred while running alerts.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


class DismissAlertView(APIView):
    """
    API endpoint to dismiss an alert for the authenticated user.
    
    Authentication required: JWT
    Permission required: IsAuthenticated
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    endpoint = "dismiss/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to dismiss a specific alert.
        
        Query parameters:
            channel_send_id: The ID of the channel send to dismiss
            
        Returns:
            Response with empty message on success or error message
        """
        try:
            alerts.util.dismiss_alert(request.query_params.get("channel_send_id", None))
            return ret_message("")
        except Exception as e:
            return ret_message(
                "An error occurred while dismissing alert.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


class AlertTypesView(APIView):
    """
    API endpoint to alert types.

    Authentication required: JWT
    Permission required: attendance or meetings

    GET: Returns all alert types for the current season
    POST: Creates or updates an alert type
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "alert_types/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to retrieve all alert types.

        Returns:
            Response with list of alert types or error message
        """

        def fun():
            alert_type_id = request.query_params.get("id", None)

            alert_types = alerts.util.get_alert_types(alert_type_id)
            serializer = AlertTypeSerializer(alert_types, many=alert_type_id is None)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj_admin,
            "An error occurred while getting alert types.",
            fun,
        )

    def post(self, request, format=None) -> Response:
        """
        POST endpoint to create or update an alert type.

        Request body: AlertType object with title, description, etc.

        Returns:
            Success message or error response
        """

        def fun():
            serializer = AlertTypeSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            alert_type = alerts.util.save_alert_type(serializer.validated_data)
            return Response(AlertTypeSerializer(alert_type).data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj_admin,
            "An error occurred while saving alert type.",
            fun,
        )


# Backward compatibility aliases (can be removed in future versions)
StageAlerts = StageAlertsView
SendAlerts = SendAlertsView
RunAlerts = RunAlertsView
DismissAlert = DismissAlertView
