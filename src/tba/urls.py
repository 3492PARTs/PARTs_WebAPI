from django.urls import path
from .views import (
    SyncSeasonView,
    SyncEventView,
    SyncMatchesView,
    SyncEventTeamInfoView,
    WebhookView,
)

app_name = "tba"

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("sync-season/", SyncSeasonView.as_view(), name="sync-season"),
    path("sync-event/", SyncEventView.as_view(), name="sync-event"),
    path("sync-matches/", SyncMatchesView.as_view(), name="sync-matches"),
    path("sync-event-team-info/", SyncEventTeamInfoView.as_view(), name="sync-event-team-info"),
    path("webhook/", WebhookView.as_view(), name="webhook"),
]
