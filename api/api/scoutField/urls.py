from django.urls import path
from .views import *

urlpatterns = [
    path('GetQuestions/', GetQuestions.as_view()),
    path('PostSaveAnswers/', PostSaveAnswers.as_view()),
    path('GetResults/', GetResults.as_view()),
]
