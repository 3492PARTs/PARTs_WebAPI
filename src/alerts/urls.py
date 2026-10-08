from django.urls import path

from alerts.views import AlertTypesView, RunAlertsView, StageAlertsView, SendAlertsView, DismissAlertView

app_name = "alerts"

urlpatterns = [
    path("run/", RunAlertsView.as_view(), name="run"),
    path("stage/", StageAlertsView.as_view(), name="stage"),
    path("send/", SendAlertsView.as_view(), name="send"),
    path("dismiss/", DismissAlertView.as_view(), name="dismiss"),
    path("types/", AlertTypesView.as_view(), name="types"),
]
