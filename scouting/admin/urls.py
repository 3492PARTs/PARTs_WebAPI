from django.urls import path
from .views import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("scout-auth-group/", ScoutAuthGroupsView.as_view()),
    path("season/", SeasonView.as_view()),
    path("event/", EventView.as_view()),
    path("team/", TeamView.as_view()),
    path("set-season-event/", SetSeasonEventView.as_view()),
    path("team-to-event/", TeamToEventView.as_view()),
    path("remove-team-to-event/", RemoveTeamToEventView.as_view()),
    path("scout-field-schedule/", ScoutFieldScheduleView.as_view()),
    path("notify-user/", NotifyUserView.as_view()),
    path("schedule/", ScheduleView.as_view()),
    path("scouting-user-info/", ScoutingUserInfoView.as_view()),
    path("delete-field-result/", FieldResponseView.as_view()),
    path("delete-pit-result/", PitResponseView.as_view()),
    path("toggle-scout-under-review/", ToggleScoutUnderReviewView.as_view()),
    path("mark-scout-present/", MarkScoutPresentView.as_view()),
]
