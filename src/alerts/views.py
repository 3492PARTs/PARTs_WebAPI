from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import alerts.util_alert_definitions
from alerts.util import (
    send_alerts,
    dismiss_alert,
)
from general.security import ret_message

app_url = "alerts/"


class StageAlertsView(APIView):
    """API endpoint to stage user alerts"""

    endpoint = "stage/"

    def get(self, request, format=None):

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
    """API endpoint to notify users"""

    endpoint = "send/"

    def get(self, request, format=None):
        try:
            ret = "SEND ALERTS: "
            ret += send_alerts()
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
    """API endpoint to stage and send"""

    endpoint = "run/"

    def get(self, request, format=None):
        try:
            ret = "RUN ALERTS: "
            ret += "STAGE ALERTS: "
            ret += alerts.util_alert_definitions.stage_alerts()
            ret += "SEND ALERTS: "
            ret += send_alerts()
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
    """API endpoint to dismiss an alert"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    endpoint = "dismiss/"

    def get(self, request, format=None):
        try:
            dismiss_alert(request.query_params.get("channel_send_id", None))
            return ret_message("")
        except Exception as e:
            return ret_message(
                "An error occurred while dismissing alert.",
                True,
                app_url + self.endpoint,
                -1,
                e,
            )


# Backward compatibility aliases (can be removed in future versions)
StageAlerts = StageAlertsView
SendAlerts = SendAlertsView
RunAlerts = RunAlertsView
DismissAlert = DismissAlertView
