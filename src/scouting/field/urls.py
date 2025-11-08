from django.urls import path
from .views import (
    FormView,
    ResponseColumnsView,
    ResponsesView,
    CheckInView,
)

app_name = "scouting_field"

urlpatterns = [
    path("responses/", ResponsesView.as_view(), name="responses"),
    path("check-in/", CheckInView.as_view(), name="check-in"),
    path("form/", FormView.as_view(), name="form"),
    # path("scouting-responses/", ScoutingResponsesView.as_view()),
    path("response-columns/", ResponseColumnsView.as_view(), name="response-columns"),
]
