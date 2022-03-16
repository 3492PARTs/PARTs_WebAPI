from django.urls import re_path, include

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Scout Field Endpoints
    re_path(r'^scoutField/', include('api.api.scoutField.urls')),
    # Scout Pit Endpoints
    re_path(r'^scoutPit/', include('api.api.scoutPit.urls')),
    # Scout Admin Endpoints;
    re_path(r'^scoutAdmin/', include('api.api.scoutAdmin.urls')),
    # Scout Portal Endpoints
    re_path(r'^scoutPortal/', include('api.api.scoutPortal.urls')),
    # Admin Endpoints
    re_path(r'^admin/', include('api.api.admin.urls')),
    # Admin Endpoints
    #re_path(r'^tba/', include('api.api.tba.urls'))
    # Competition Endpoints
    re_path(r'^competition/', include('api.api.competition.urls'))
]
