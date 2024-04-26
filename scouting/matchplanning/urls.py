from django.urls import path
from .views import *

urlpatterns = [
    path("team-notes/", TeamNotes.as_view()),
]
