from django.urls import include, path
from .views import APIStatus

urlpatterns = [
    path("api-status/", APIStatus.as_view()),
    path("competition/", include("public.competition.urls")),
]
