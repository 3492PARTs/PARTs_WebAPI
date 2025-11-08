from django.urls import path

from attendance.views import (
    AttendanceView,
    MeetingsView,
    AttendanceReportView,
    MeetingHoursView,
)

app_name = "attendance"

urlpatterns = [
    path("attendance/", AttendanceView.as_view(), name="attendance"),
    path("meetings/", MeetingsView.as_view(), name="meetings"),
    path("attendance-report/", AttendanceReportView.as_view(), name="attendance-report"),
    path("meeting-hours/", MeetingHoursView.as_view(), name="meeting-hours"),
]
