from django.urls import path
from .views import *

urlpatterns = [
    path('questions/', Questions.as_view()),
    #path('save-answers/', SaveAnswers.as_view()),
    path('results/', Results.as_view()),
]
