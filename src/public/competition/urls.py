from django.urls import path
from .views import InitView

app_name = "competition"

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('init/', InitView.as_view(), name="init")
]
