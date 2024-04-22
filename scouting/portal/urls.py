from django.urls import path
from .views import SaveScheduleEntry, NotifyUser

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("save-schedule-entry/", SaveScheduleEntry.as_view()),
    path("notify-user/", NotifyUser.as_view()),
]
