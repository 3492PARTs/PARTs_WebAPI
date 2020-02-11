from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from api.api.views.scoutField import *
from api.api.views.scoutPit import *
from api.api.views.scoutAdmin import *
from api.api.views.scoutPortal import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('get_scout_field_questions/', GetScoutFieldInputs.as_view()),
    path('post_save_scout_field_answers/', PostScoutFieldSaveAnswers.as_view()),
    path('get_scout_field_results/', GetScoutFieldQuery.as_view()),
    path('get_scout_pit_questions/', GetScoutPitInputs.as_view()),
    path('post_save_scout_pit_answers/', PostScoutPitSaveAnswers.as_view()),
    path('post_save_scout_pit_picture/', PostScoutPitSavePicture.as_view()),
    path('get_scout_pit_results_init/', GetScoutPitResultInit.as_view()),
    path('post_get_scout_pit_results/', PostScoutPitGetResults.as_view()),
    path('get_scout_admin_init/', GetScoutAdminInit.as_view()),
    path('get_sync_season/', GetScoutAdminSyncSeason.as_view()),
    path('get_set_season/', GetScoutAdminSetSeason.as_view()),
    path('get_add_season/', GetScoutAdminAddSeason.as_view()),
    path('get_delete_season/', GetScoutAdminDeleteSeason.as_view()),
    path('get_scout_question_init/', GetScoutAdminQuestionInit.as_view()),
    path('post_save_scout_question/', PostScoutAdminSaveScoutQuestion.as_view()),
    path('post_update_scout_question/', PostScoutAdminUpdateScoutQuestion.as_view()),
    path('get_toggle_scout_question/', GetScoutAdminToggleScoutQuestion.as_view()),
    path('get_toggle_option/', GetScoutAdminToggleOption.as_view()),
    path('post_save_user/', PostScoutAdminSaveUser.as_view()),
    path('post_save_scout_schedule_entry/', PostScoutAdminSaveScoutScheduleEntry.as_view()),
    path('post_notify_users/', PostScoutAdminNotifyUser.as_view()),
    path('post_save_phone_type/', PostScoutAdminSavePhoneType.as_view()),
    path('get_scout_portal_init/', GetScoutPortalInit.as_view()),
]
