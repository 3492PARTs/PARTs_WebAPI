from django.urls import path

from alerts.views import RunAlerts, StageAlerts, SendAlerts, DismissAlert

urlpatterns = [
    path("attendance/", RunAlerts.as_view()),
]
