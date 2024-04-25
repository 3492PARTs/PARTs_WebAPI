from django.urls import path
from .views import *

urlpatterns = [
    path("init/", Init.as_view()),
    path("save-note/", SaveNote.as_view()),
    path("load-team-notes/", LoadTeamNotes.as_view()),
]
