from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from api.api.views.scoutField import *
from api.api.views.scoutAdmin import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('get_scout_field_questions/', GetScoutFieldInputs.as_view()),
    path('get_scout_admin_init/', GetScoutAdminInit.as_view()),
    path('get_sync_season/', GetScoutAdminSyncSeason.as_view()),
    path('get_set_season/', GetScoutAdminSetSeason.as_view()),
    path('get_add_season/', GetScoutAdminAddSeason.as_view()),
    path('get_delete_season/', GetScoutAdminDeleteSeason.as_view()),
    path('post_save_scout_field_question/', PostSaveScoutFieldQuestionAnswers.as_view()),
    path('post_update_scout_field_question/', PostUpdateScoutFieldQuestionAnswers.as_view()),
    path('get_delete_scout_field_question/', GetScoutAdminDeleteScoutFieldQuestion.as_view()),
    path('get_toggle_option/', GetScoutAdminToggleOption.as_view()),
    path('post_save_scout_pit_question/', PostSaveScoutPitQuestionAnswers.as_view()),
    path('post_update_scout_pit_question/', PostUpdateScoutPitQuestionAnswers.as_view()),
    path('get_delete_scout_pit_question/', GetScoutAdminDeleteScoutPitQuestion.as_view())
]
