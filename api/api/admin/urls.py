from django.urls import path
from api.api.admin.views import *

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('get_init/', GetInit.as_view()),
    path('get_log/', GetErrors.as_view()),
]
