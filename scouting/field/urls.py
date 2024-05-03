from django.urls import path
from .views import *

urlpatterns = [
    path("responses/", ResponsesView.as_view()),
    path("check-in/", CheckInView.as_view()),
]
