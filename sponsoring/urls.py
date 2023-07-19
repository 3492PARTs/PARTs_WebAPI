from django.urls import path

from .views import SaveAnswers, GetFormInit, SaveQuestion, GetQuestions

urlpatterns = [
    path('get-questions/', GetQuestions.as_view()),
    path('save-answers/', SaveAnswers.as_view()),
    path('form-init/', GetFormInit.as_view()),
    path('save-question/', SaveQuestion.as_view()),
]
