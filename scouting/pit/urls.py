from django.urls import path
from .views import *

urlpatterns = [
    path("save-picture/", SavePicture.as_view()),
    path("results-init/", ResultsInit.as_view()),
    path("results/", Results.as_view()),
    path("team-data/", TeamData.as_view()),
    path("set-default-pit-image/", SetDefaultPitImage.as_view()),
]
