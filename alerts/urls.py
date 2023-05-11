from django.urls import include, path

from alerts.views import RunAlerts, SendAlerts, DismissAlert

urlpatterns = [
    path('run/', RunAlerts.as_view()),
    path('send/', SendAlerts.as_view()),
    path('dismiss/', DismissAlert.as_view()),
]
