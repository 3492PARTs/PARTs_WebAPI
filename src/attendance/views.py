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
    """
    API endpoint to manage attendance records.

    Authentication required: JWT
    Permission required: attendance

    GET: Returns attendance records filtered by user and/or meeting
    POST: Creates or updates an attendance entry
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "attendance/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to retrieve attendance records.

        Query parameters:
            user_id: Optional user ID to filter by
            meeting_id: Optional meeting ID to filter by

        Returns:
            Response with list of attendance records or error message
        """

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

    def post(self, request, format=None) -> Response:
        """
        POST endpoint to create or update an attendance entry.

        Request body: Attendance object with user, meeting, time_in, time_out, etc.

        Returns:
            Success message or error response
        """

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
    """
    API endpoint to manage meetings.

    Authentication required: JWT
    Permission required: attendance or meetings

    GET: Returns all meetings for the current season
    POST: Creates or updates a meeting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "meetings/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to retrieve all meetings.

        Returns:
            Response with list of meetings or error message
        """

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

    def post(self, request, format=None) -> Response:
        """
        POST endpoint to create or update a meeting.

        Request body: Meeting object with title, description, start, end, meeting_typ, etc.

        Returns:
            Success message or error response
        """

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
    """
    API endpoint to get attendance reports showing hours and percentages.

    Authentication required: JWT
    Permission required: attendance

    GET: Returns attendance report for users
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "attendance-report/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to retrieve attendance report.

        Query parameters:
            user_id: Optional user ID to filter by
            meeting_id: Optional meeting ID to filter by

        Returns:
            Response with attendance statistics or error message
        """

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
    """
    API endpoint to get total meeting hours for the current season.

    Authentication required: JWT
    Permission required: attendance

    GET: Returns total hours, bonus hours, and event hours
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "meeting-hours/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to retrieve total meeting hours.

        Returns:
            Response with hours, bonus_hours, and event_hours or error message
        """

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


class EndMeetingView(APIView):
    """
    API endpoint to end a meeting.

    Authentication required: JWT
    Permission required: attendance

    GET: Returns success message after ending the meeting
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "meeting-hours/"

    def get(self, request, format=None) -> Response:
        """
        GET endpoint to end a meeting.

        Returns:
            Response success message
        """

        def fun():
            attendance.util.end_meeting(request.query_params.get("meeting_id", None))
            return ret_message("Meeting ended successfully.")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while ending the meeting.",
            fun,
        )
