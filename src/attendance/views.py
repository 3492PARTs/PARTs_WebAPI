from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

import attendance.util
from general.security import ret_message, access_response
from attendance.serializers import (
    AttendanceSerializer,
    MeetingSerializer,
    AttendanceReportSerializer,
    MeetingHoursSerializer,
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
        def fun():
            att = attendance.util.get_attendance(
                request.query_params.get("user_id", None),
                request.query_params.get("meeting_id", None),
            )
            serializer = AttendanceSerializer(att, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting attendance.",
            fun,
        )

    def post(self, request, format=None):
        def fun():
            serializer = AttendanceSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            attendance.util.save_attendance(serializer.validated_data)
            return ret_message("Saved attendance entry.")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while saving attendance entry.",
            fun,
        )


class MeetingsView(APIView):
    """API endpoint to manage meetings"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "meetings/"

    def get(self, request, format=None):
        def fun():
            mtgs = attendance.util.get_meetings()
            serializer = MeetingSerializer(mtgs, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            [auth_obj, auth_obj_meeting],
            "An error occurred while getting meetings.",
            fun,
        )

    def post(self, request, format=None):
        def fun():
            serializer = MeetingSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            attendance.util.save_meeting(serializer.validated_data)
            return ret_message("Saved meeting entry.")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj_meeting,
            "An error occurred while saving meeting entry.",
            fun,
        )


class AttendanceReportView(APIView):
    """API endpoint to get the attendance report"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "attendance-report/"

    def get(self, request, format=None):
        def fun():
            att = attendance.util.get_attendance_report(
                request.query_params.get("user_id", None),
                request.query_params.get("meeting_id", None),
            )
            serializer = AttendanceReportSerializer(att, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting the attendance report.",
            fun,
        )


class MeetingHoursView(APIView):
    """API endpoint to get total number of meetings"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "meeting-hours/"

    def get(self, request, format=None):
        def fun():
            serializer = MeetingHoursSerializer(attendance.util.get_meeting_hours())
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting the total meeting hours.",
            fun,
        )
