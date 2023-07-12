from django.urls import include
from django.urls import path
from rest_framework import routers
from .views import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('init/', Init.as_view()),
    path('sync-season/', SyncSeason.as_view()),
    path('set-season/', SetSeason.as_view()),
    path('toggle-competition-page/', ToggleCompetitionPage.as_view()),
    path('sync-matches/', SyncMatches.as_view()),
    path('sync-event-team-info/', SyncEventTeamInfo.as_view()),
    path('add-season/', AddSeason.as_view()),
    path('delete-season/', DeleteSeason.as_view()),
    path('add-event/', AddEvent.as_view()),
    path('add-team/', AddTeam.as_view()),
    path('delete-event/', DeleteEvent.as_view()),
    path('add-team-to-event/', AddTeamToEvent.as_view()),
    path('remove-team-to-event/', RemoveTeamToEvent.as_view()),
    #path('scout-question-init/', QuestionInit.as_view()),
    #path('save-scout-question/', SaveScoutQuestion.as_view()),
    #path('update-scout-question/', UpdateScoutQuestion.as_view()),
    path('toggle-scout-question/', ToggleScoutQuestion.as_view()),
    path('toggle-option/', ToggleOption.as_view()),
    path('save-scout-field-schedule-entry/',
         SaveScoutFieldScheduleEntry.as_view()),
    path('notify-users/', NotifyUsers.as_view()),
    path('save-phone-type/', SavePhoneType.as_view()),
]
