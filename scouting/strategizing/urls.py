from django.urls import path
from .views import *

urlpatterns = [
    path("team-notes/", TeamNoteView.as_view()),
    path("match-strategy/", MatchStrategyView.as_view()),
    path("alliance-selection/", AllianceSelectionView.as_view()),
    path("graph-team/", GraphTeamView.as_view()),
]
