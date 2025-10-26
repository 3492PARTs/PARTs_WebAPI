from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

import attendance.util
from general.security import ret_message, has_access
from attendance.serializers import (
    AttendanceSerializer,
    MeetingSerializer,
    AttendanceReportSerializer,
)

app_url = "attendance/"
auth_obj = "attendance"
auth_obj_meeting = "meetings"


class AttendanceView(APIView):
    """API endpoint to take attendance"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "attendance/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                att = attendance.util.get_attendance(
                    request.query_params.get("user_id", None),
                    request.query_params.get("meeting_id", None),
                )
                serializer = AttendanceSerializer(att, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting attendance.",
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


class MeetingsView(APIView):
    """API endpoint to manage meetings"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "meetings/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj) or has_access(
            request.user.id, auth_obj_meeting
        ):
            try:
                mtgs = attendance.util.get_meetings()
                serializer = MeetingSerializer(mtgs, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting meetings.",
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
        if has_access(request.user.id, auth_obj_meeting):
            serializer = MeetingSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            try:
                attendance.util.save_meeting(serializer.validated_data)
                return ret_message("Saved meeting entry.")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving meeting entry.",
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


class AttendanceReportView(APIView):
    """API endpoint to take attendance"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "attendance-report/"

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                att = attendance.util.get_attendance_report(
                    request.query_params.get("user_id", None),
                    request.query_params.get("meeting_id", None),
                )
                serializer = AttendanceReportSerializer(att, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting the attendance report.",
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
