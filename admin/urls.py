from django.urls import path
from .views import Init, SaveUser, ErrorLogView

urlpatterns = [
    path('init/', Init.as_view()),
    path('save-user/', SaveUser.as_view()),
    path('error-log/', ErrorLogView.as_view()),
]
