from django.urls import include, path

from . import views

urlpatterns = [
    path("season/", views.Season.as_view()),
    path("event/", views.Event.as_view()),
    path("team/", views.Team.as_view()),
    path("match/", views.Match.as_view()),
    path("schedule/", views.Schedule.as_view()),
    path("scout-field-schedule/", views.ScoutFieldSchedule.as_view()),
    path("schedule-type/", views.ScheduleType.as_view()),
    path("all-scouting-info/", views.AllScoutingInfo.as_view()),
    path("portal/", include("scouting.portal.urls")),
    path("pit/", include("scouting.pit.urls")),
    path("field/", include("scouting.field.urls")),
    path("admin/", include("scouting.admin.urls")),
    path("match-planning/", include("scouting.matchplanning.urls")),
]
