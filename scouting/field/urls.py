from django.urls import path
from .views import *

urlpatterns = [
    path("init/", Init.as_view()),
    # path('save-answers/', SaveAnswers.as_view()),
    path("responses/", Responses.as_view()),
    path("removed-responses/", RemovedResponses.as_view()),
    path("check-in/", CheckIn.as_view()),
]
