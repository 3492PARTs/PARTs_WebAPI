from django.urls import include, path

from . import views

app_name = "scouting"

urlpatterns = [
    path("season/", views.SeasonView.as_view(), name="season"),
    path("event/", views.EventView.as_view(), name="event"),
    path("team/", views.TeamView.as_view(), name="team"),
    path("match/", views.MatchView.as_view(), name="match"),
    path("schedule/", views.ScheduleView.as_view(), name="schedule"),
    path("scout-field-schedule/", views.ScoutFieldScheduleView.as_view(), name="scout-field-schedule"),
    path("schedule-type/", views.ScheduleTypeView.as_view(), name="schedule-type"),
    path("all-scouting-info/", views.AllScoutingInfoView.as_view(), name="all-scouting-info"),
    path("portal/", include("scouting.portal.urls")),
    path("pit/", include("scouting.pit.urls")),
    path("field/", include("scouting.field.urls")),
    path("admin/", include("scouting.admin.urls")),
    path("strategizing/", include("scouting.strategizing.urls")),
]
