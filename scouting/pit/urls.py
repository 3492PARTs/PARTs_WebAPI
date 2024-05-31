from django.urls import path
from .views import *

urlpatterns = [
    path("save-picture/", SavePictureView.as_view()),
    path("responses/", ResponsesView.as_view()),
    path("team-data/", TeamDataView.as_view()),
    path("set-default-pit-image/", SetDefaultPitImageView.as_view()),
]
