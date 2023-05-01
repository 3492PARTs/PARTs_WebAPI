from django.urls import include, path

from alerts.views import RunAlerts

urlpatterns = [
    path('run/', RunAlerts.as_view()),
]
