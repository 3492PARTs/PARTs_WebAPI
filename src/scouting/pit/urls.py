from django.urls import path
from .views import (
    SavePictureView,
    ResponsesView,
    TeamDataView,
    SetDefaultPitImageView,
)

app_name = "scouting_pit"

urlpatterns = [
    path("save-picture/", SavePictureView.as_view(), name="save-picture"),
    path("responses/", ResponsesView.as_view(), name="responses"),
    path("team-data/", TeamDataView.as_view(), name="team-data"),
    path("set-default-pit-image/", SetDefaultPitImageView.as_view(), name="set-default-pit-image"),
]
