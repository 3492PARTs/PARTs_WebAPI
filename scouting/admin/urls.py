from django.urls import path
from .views import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("scout-auth-group/", ScoutAuthGroupsView.as_view()),
    path("sync-season/", SyncSeasonView.as_view()),
    path("sync-event/", SyncEventView.as_view()),
    path("set-season/", SetSeason.as_view()),
    path("toggle-competition-page/", ToggleCompetitionPage.as_view()),
    path("sync-matches/", SyncMatchesView.as_view()),
    path("sync-event-team-info/", SyncEventTeamInfoView.as_view()),
    path("season/", SeasonView.as_view()),
    path("delete-season/", DeleteSeason.as_view()),
    path("add-event/", AddEvent.as_view()),
    path("add-team/", AddTeam.as_view()),
    path("delete-event/", DeleteEvent.as_view()),
    path("add-team-to-event/", AddTeamToEvent.as_view()),
    path("remove-team-to-event/", RemoveTeamToEvent.as_view()),
    path("save-scout-field-schedule-entry/", SaveScoutFieldScheduleEntry.as_view()),
    path("notify-user/", NotifyUser.as_view()),
    path("save-schedule-entry/", SaveScheduleEntry.as_view()),
    path("scouting-user-info/", ScoutingUserInfo.as_view()),
    path("delete-field-result/", DeleteFieldResult.as_view()),
    path("delete-pit-result/", DeletePitResult.as_view()),
    path("toggle-scout-under-review/", ToggleScoutUnderReview.as_view()),
    path("mark-scout-present/", MarkScoutPresent.as_view()),
]
