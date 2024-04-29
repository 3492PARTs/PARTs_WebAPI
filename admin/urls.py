from django.urls import path
from .views import ErrorLogView, ScoutAuthGroupsView, PhoneType

urlpatterns = [
    path('error-log/', ErrorLogView.as_view()),
    path('scout-auth-groups/', ScoutAuthGroupsView.as_view()),
    path('phone-type/', PhoneType.as_view()),
]
