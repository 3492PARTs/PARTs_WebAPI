from django.urls import path
from .views import *

urlpatterns = [
    path('init/', Init.as_view()),
]
