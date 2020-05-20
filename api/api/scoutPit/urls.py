from django.urls import path
from .views import *

urlpatterns = [
    path('GetQuestions/', GetQuestions.as_view()),
    path('PostSaveAnswers/', PostSaveAnswers.as_view()),
    path('PostSavePicture/', PostSavePicture.as_view()),
    path('GetResultsInit/', GetResultsInit.as_view()),
    path('PostGetResults/', PostGetResults.as_view()),
    path('GetTeamData/', GetTeamData.as_view())
]