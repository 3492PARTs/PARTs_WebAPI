from django.urls import path

from sponsoring.views import GetItems, GetSponsors, SaveSponsor, SaveItem, SaveSponsorOrder

urlpatterns = [
    path('get-items/', GetItems.as_view()),
    path('get-sponsors/', GetSponsors.as_view()),
    path('save-sponsor/', SaveSponsor.as_view()),
    path('save-item/', SaveItem.as_view()),
    path('save-sponsor-order/', SaveSponsorOrder.as_view()),
]
