from django.urls import path
from .views import Init, ErrorLogView

urlpatterns = [
    path('init/', Init.as_view()),
    path('error-log/', ErrorLogView.as_view()),
]
