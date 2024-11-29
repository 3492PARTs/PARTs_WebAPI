from django.urls import path
from .views import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("sync-season/", SyncSeasonView.as_view()),
    path("sync-event/", SyncEventView.as_view()),
    path("sync-matches/", SyncMatchesView.as_view()),
    path("sync-event-team-info/", SyncEventTeamInfoView.as_view()),
    path("webhook/", Webhook.as_view()),
]
