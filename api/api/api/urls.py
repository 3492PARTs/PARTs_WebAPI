from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from api.api import views

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('query-params/', views.MainQueryParameters.as_view()),
    path('query/', views.GetData.as_view()),
    path('insert/', views.InsertData.as_view())
]
