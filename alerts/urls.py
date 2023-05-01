from django.urls import include, path

from alerts.views import RunAlerts, SendAlerts

urlpatterns = [
    path('run/', RunAlerts.as_view()),
    path('send/', SendAlerts.as_view()),
]
