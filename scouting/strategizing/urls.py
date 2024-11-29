from django.urls import path
from .views import *

urlpatterns = [
    path("team-notes/", TeamNotesView.as_view()),
]
