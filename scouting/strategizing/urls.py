from django.urls import path
from .views import *

urlpatterns = [
    path("team-notes/", TeamNoteView.as_view()),
    path("match-strategy/", MatchStrategyView.as_view())
]
