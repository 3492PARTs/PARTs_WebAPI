from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from api.api.views.scoutField import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('get_scout_field_questions/', GetScoutFieldInputs.as_view())
]
