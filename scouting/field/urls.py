from django.urls import path
from .views import *

urlpatterns = [
    path("init/", Init.as_view()),
    # path('save-answers/', SaveAnswers.as_view()),
    path("results/", Results.as_view()),
    path("check-in/", CheckIn.as_view()),
]
