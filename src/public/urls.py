from django.urls import include, path
from .views import APIStatusView

app_name = "public"

urlpatterns = [
    path("api-status/", APIStatusView.as_view(), name="api-status"),
    path("competition/", include("public.competition.urls")),
    path("season/", include("public.season.urls")),
]
