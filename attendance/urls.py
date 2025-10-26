from django.urls import path

from attendance.views import AttendanceView, MeetingsView, AttendanceReportView

urlpatterns = [
    path("attendance/", AttendanceView.as_view()),
    path("meetings/", MeetingsView.as_view()),
    path("attendance-report/", AttendanceReportView.as_view()),
]
