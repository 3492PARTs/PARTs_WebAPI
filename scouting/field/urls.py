from django.urls import path
from .views import *

urlpatterns = [
    path("responses/", Responses.as_view()),
    path("check-in/", CheckIn.as_view()),
]
