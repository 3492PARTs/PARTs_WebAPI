from django.urls import path

from attendance.views import AttendanceView, MeetingsView

urlpatterns = [
    path("attendance/", AttendanceView.as_view()),
    path("meetings/", MeetingsView.as_view()),
]
