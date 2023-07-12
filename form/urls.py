from django.urls import path

from .views import SaveAnswers, GetFormInit, SaveQuestion


urlpatterns = [
    path('save-answers/', SaveAnswers.as_view()),
    path('form-init/', GetFormInit.as_view()),
    path('save-question/', SaveQuestion.as_view()),
]
