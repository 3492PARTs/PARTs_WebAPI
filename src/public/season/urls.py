from django.urls import path
from .views import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [path("current/", CurrentSeasonView.as_view())]
