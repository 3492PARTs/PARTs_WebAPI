from django.urls import path

from sponsoring.views import GetItemsView, GetSponsorsView, SaveSponsorView, SaveItemView, SaveSponsorOrderView

urlpatterns = [
    path('get-items/', GetItemsView.as_view()),
    path('get-sponsors/', GetSponsorsView.as_view()),
    path('save-sponsor/', SaveSponsorView.as_view()),
    path('save-item/', SaveItemView.as_view()),
    path('save-sponsor-order/', SaveSponsorOrderView.as_view()),
]
