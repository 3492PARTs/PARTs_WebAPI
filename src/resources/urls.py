from django.urls import path

from resources.views import (
    ResourceTypesView,
    ResourcesView,
    ResourceCheckOutsView,
    CheckOutResourceView,
    CheckInResourceView,
)

app_name = "resources"

urlpatterns = [
    path("resource-types/", ResourceTypesView.as_view(), name="resource-types"),
    path("resources/", ResourcesView.as_view(), name="resources"),
    path(
        "resource-checkouts/",
        ResourceCheckOutsView.as_view(),
        name="resource-checkouts",
    ),
    path("check-out/", CheckOutResourceView.as_view(), name="check-out"),
    path("check-in/", CheckInResourceView.as_view(), name="check-in"),
]
