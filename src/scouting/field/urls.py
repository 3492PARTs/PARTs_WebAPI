from django.urls import path
from .views import *

urlpatterns = [
    path("responses/", ResponsesView.as_view()),
    path("check-in/", CheckInView.as_view()),
    path("form/", FormView.as_view()),
    # path("scouting-responses/", ScoutingResponsesView.as_view()),
    path("response-columns/", ResponseColumnsView.as_view()),
]
