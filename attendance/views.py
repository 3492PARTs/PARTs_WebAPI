from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

import attendance.util
from general.security import ret_message, has_access
from attendance.serializers import AttendanceSerializer

app_url = "attendance/"
auth_obj = "attendance"


class Attendance(APIView):
    """API endpoint to take attendance"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "attendance/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                att = attendance.util.get_attendance()
                serializer = AttendanceSerializer(att, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while attendance.",
                    True,
                    app_url + self.endpoint,
                    -1,
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
        if has_access(request.user.id, auth_obj):
            serializer = AttendanceSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            try:
                attendance.util.save_attendance(serializer.validated_data)
                return ret_message("Saved attendance entry.")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving attendance entry.",
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
