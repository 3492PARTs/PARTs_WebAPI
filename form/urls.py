from django.urls import path

from .views import SaveAnswers

urlpatterns = [
    path('save-answers/', SaveAnswers.as_view()),
]
