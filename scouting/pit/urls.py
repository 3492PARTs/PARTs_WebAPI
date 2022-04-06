from django.urls import path
from .views import *

urlpatterns = [
    path('questions/', Questions.as_view()),
    path('save-answers/', SaveAnswers.as_view()),
    path('save-picture/', SavePicture.as_view()),
    path('results-init/', ResultsInit.as_view()),
    path('results/', Results.as_view()),
    path('team-data/', TeamData.as_view())
]
