from rest_framework.views import APIView

from alerts.util import stage_all_field_schedule_alerts, stage_schedule_alerts, send_alerts
from general.security import ret_message

app_url = 'alerts/'


class RunAlerts(APIView):
    """API endpoint to stage user alerts"""

    endpoint = 'run/'

    def get(self, request, format=None):

        try:
            ret = 'all field alerts\n'
            ret += stage_all_field_schedule_alerts()
            ret += 'schedule alerts\n'
            ret += stage_schedule_alerts()
            return ret_message(ret)
        except Exception as e:
            return ret_message('An error occurred while running alerts.', True, app_url + self.endpoint,
                               0, e)


class SendAlerts(APIView):
    """API endpoint to notify users"""

    endpoint = 'send/'

    def get(self, request, format=None):
        send_alerts()
        try:
            ret = 'send alerts\n'
            ret += send_alerts()
            return ret_message(ret)
        except Exception as e:
            return ret_message('An error occurred while sending alerts.', True, app_url + self.endpoint,
                               0, e)