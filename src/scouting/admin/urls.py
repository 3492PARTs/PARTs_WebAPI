from django.urls import path
from .views import (
    ScoutAuthGroupsView,
    SeasonView,
    EventView,
    TeamView,
    MatchView,
    SetSeasonEventView,
    TeamToEventView,
    RemoveTeamToEventView,
    ScoutFieldScheduleView,
    NotifyUserView,
    ScheduleView,
    ScoutingUserInfoView,
    FieldResponseView,
    PitResponseView,
    MarkScoutPresentView,
    FieldFormView,
    ScoutingReportView,
)

app_name = "scouting_admin"

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("scout-auth-group/", ScoutAuthGroupsView.as_view(), name="scout-auth-group"),
    path("season/", SeasonView.as_view(), name="season"),
    path("event/", EventView.as_view(), name="event"),
    path("team/", TeamView.as_view(), name="team"),
    path("match/", MatchView.as_view(), name="match"),
    path("set-season-event/", SetSeasonEventView.as_view(), name="set-season-event"),
    path("team-to-event/", TeamToEventView.as_view(), name="team-to-event"),
    path("remove-team-to-event/", RemoveTeamToEventView.as_view(), name="remove-team-to-event"),
    path("scout-field-schedule/", ScoutFieldScheduleView.as_view(), name="scout-field-schedule"),
    path("notify-user/", NotifyUserView.as_view(), name="notify-user"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("scouting-user-info/", ScoutingUserInfoView.as_view(), name="scouting-user-info"),
    path("delete-field-result/", FieldResponseView.as_view(), name="delete-field-result"),
    path("delete-pit-result/", PitResponseView.as_view(), name="delete-pit-result"),
    path("mark-scout-present/", MarkScoutPresentView.as_view(), name="mark-scout-present"),
    path("field-form/", FieldFormView.as_view(), name="field-form"),
    path("scouting-report/", ScoutingReportView.as_view(), name="scouting-report"),
]
