from django.urls import path
from .views import (
    TeamNoteView,
    MatchStrategyView,
    AllianceSelectionView,
    GraphTeamView,
    DashboardView,
    DashboardViewTypeView,
)

app_name = "scouting_strategizing"

urlpatterns = [
    path("team-notes/", TeamNoteView.as_view(), name="team-notes"),
    path("match-strategy/", MatchStrategyView.as_view(), name="match-strategy"),
    path("alliance-selection/", AllianceSelectionView.as_view(), name="alliance-selection"),
    path("graph-team/", GraphTeamView.as_view(), name="graph-team"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard-view-types/", DashboardViewTypeView.as_view(), name="dashboard-view-types"),
]
