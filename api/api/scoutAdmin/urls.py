from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from .views import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('GetInit/', GetInit.as_view()),
    path('GetSyncSeason/', GetSyncSeason.as_view()),
    path('GetSetSeason/', GetSetSeason.as_view()),
    path('GetAddSeason/', GetAddSeason.as_view()),
    path('GetDeleteSeason/', GetDeleteSeason.as_view()),
    path('GetScoutQuestionInit/', GetQuestionInit.as_view()),
    path('PostSaveScoutQuestion/', PostSaveScoutQuestion.as_view()),
    path('PostUpdateScoutQuestion/', PostUpdateScoutQuestion.as_view()),
    path('GetToggleScoutQuestion/', GetToggleScoutQuestion.as_view()),
    path('GetToggleOption/', GetToggleOption.as_view()),
    path('PostSaveScoutScheduleEntry/', PostSaveScoutScheduleEntry.as_view()),
    path('PostNotifyUser/', PostNotifyUser.as_view()),
    path('PostSavePhoneType/', PostSavePhoneType.as_view()),
    ]
