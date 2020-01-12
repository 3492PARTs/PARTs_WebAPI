from django.urls import path, include
from django.conf.urls import url
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import routers
from django.contrib.auth import views as auth_views
from api.auth import views

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    url(r'^get_token/', ObtainAuthToken.as_view()),
    path('register/', views.register, name='register'),
    path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
         views.activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('resend_activation/', views.resend_activation_email),
    path('user_data/', views.GetUserData.as_view()),
    path('user_links/', views.GetUserLinks.as_view()),
    path('get_user_groups/', views.GetUserGroups.as_view())
]

# TODO Proper git ignore
