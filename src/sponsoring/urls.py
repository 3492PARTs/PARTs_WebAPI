from django.urls import path

from sponsoring.views import GetItemsView, GetSponsorsView, SaveSponsorView, SaveItemView, SaveSponsorOrderView

app_name = "sponsoring"

urlpatterns = [
    path('get-items/', GetItemsView.as_view(), name="get-items"),
    path('get-sponsors/', GetSponsorsView.as_view(), name="get-sponsors"),
    path('save-sponsor/', SaveSponsorView.as_view(), name="save-sponsor"),
    path('save-item/', SaveItemView.as_view(), name="save-item"),
    path('save-sponsor-order/', SaveSponsorOrderView.as_view(), name="save-sponsor-order"),
]
