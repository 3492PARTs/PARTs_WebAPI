from django.urls import include, path

from . import views

urlpatterns = [
    path('portal/', include('scouting.portal.urls')),
    path('pit/', include('scouting.pit.urls')),
    path('field/', include('scouting.field.urls')),
    path('admin/', include('scouting.admin.urls')),
    path('match-planning/', include('scouting.matchplanning.urls')),
]
