from django.urls import path

from attendance.views import Attendance

urlpatterns = [
    path("attendance/", Attendance.as_view()),
]
