from django.urls import path
from .views import Init, ErrorLogView, ScoutAuthGroupsView, PhoneType

urlpatterns = [
    path('init/', Init.as_view()),
    path('error-log/', ErrorLogView.as_view()),
    path('scout-auth-groups/', ScoutAuthGroupsView.as_view()),
    path('phone-type/', PhoneType.as_view()),
]
