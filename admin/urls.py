from django.urls import path
from .views import Init, SaveUser, ErrorLog

urlpatterns = [
    path('init/', Init.as_view()),
    path('save-user/', SaveUser.as_view()),
    path('error-log/', ErrorLog.as_view()),
]
