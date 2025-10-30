from django.urls import path

from alerts.views import RunAlertsView, StageAlertsView, SendAlertsView, DismissAlertView

urlpatterns = [
    path("run/", RunAlertsView.as_view()),
    path("stage/", StageAlertsView.as_view()),
    path("send/", SendAlertsView.as_view()),
    path("dismiss/", DismissAlertView.as_view()),
]
