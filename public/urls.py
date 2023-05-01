from django.urls import include, path
from .views import APIStatus, NotifyUsers

urlpatterns = [
    path('api-status/', APIStatus.as_view()),
    path('competition/', include('public.competition.urls')),
    # path('notify-users/', NotifyUsers.as_view()),
]
