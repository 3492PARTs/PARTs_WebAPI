from django.urls import include, path

from . import views

urlpatterns = [
    path("season/", views.SeasonView.as_view()),
    path("event/", views.EventView.as_view()),
    path("team/", views.TeamView.as_view()),
    path("match/", views.MatchView.as_view()),
    path("schedule/", views.ScheduleView.as_view()),
    path("scout-field-schedule/", views.ScoutFieldScheduleView.as_view()),
    path("schedule-type/", views.ScheduleTypeView.as_view()),
    path("all-scouting-info/", views.AllScoutingInfoView.as_view()),
    path("portal/", include("scouting.portal.urls")),
    path("pit/", include("scouting.pit.urls")),
    path("field/", include("scouting.field.urls")),
    path("admin/", include("scouting.admin.urls")),
    path("strategizing/", include("scouting.strategizing.urls")),
]
