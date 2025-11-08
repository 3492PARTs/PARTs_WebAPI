from django.urls import path
from .views import ErrorLogView, ScoutAuthGroupsView, PhoneTypeView

app_name = "admin"

urlpatterns = [
    path('error-log/', ErrorLogView.as_view(), name="error-log"),
    path('scout-auth-groups/', ScoutAuthGroupsView.as_view(), name="scout-auth-groups"),
    path('phone-type/', PhoneTypeView.as_view(), name="phone-type"),
]
