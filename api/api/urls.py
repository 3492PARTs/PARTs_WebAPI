from django.conf.urls import url, include

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Scout Field Endpoints
    url(r'^scoutField/', include('api.api.scoutField.urls')),
    # Scout Pit Endpoints
    url(r'^scoutPit/', include('api.api.scoutPit.urls')),
    # Scout Admin Endpoints;
    url(r'^scoutAdmin/', include('api.api.scoutAdmin.urls')),
    # Scout Portal Endpoints
    url(r'^scoutPortal/', include('api.api.scoutPortal.urls')),
    # Admin Endpoints
    url(r'^admin/', include('api.api.admin.urls'))
]
