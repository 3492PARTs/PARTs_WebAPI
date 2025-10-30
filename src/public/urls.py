from django.urls import include, path
from .views import APIStatusView

urlpatterns = [
    path("api-status/", APIStatusView.as_view()),
    path("competition/", include("public.competition.urls")),
    path("season/", include("public.season.urls")),
]
