from django.urls import path

from alerts.views import RunAlerts, StageAlerts, SendAlerts, DismissAlert

urlpatterns = [
    path("run/", RunAlerts.as_view()),
    path("stage/", StageAlerts.as_view()),
    path("send/", SendAlerts.as_view()),
    path("dismiss/", DismissAlert.as_view()),
]
