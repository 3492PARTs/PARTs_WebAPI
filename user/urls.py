import webpush.views
from django.urls import path, include
from .views import UserData, UserLinksView, UserGroups, UserProfile, UserEmailConfirmation, UserEmailResendConfirmation, \
    UserRequestPasswordReset, UserPasswordReset, UserRequestUsername, \
    SaveWebPushInfo, TokenObtainPairView, TokenRefreshView, Alerts
from rest_framework_simplejwt import views as jwt_views

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    #TokenRefreshView.as_view()
    path('user-data/', UserData.as_view()),
    path('user-links/', UserLinksView.as_view()),
    path('user-groups/', UserGroups.as_view()),
    path('profile/', UserProfile.as_view()),
    path('confirm/', UserEmailConfirmation.as_view()),
    path('confirm/resend/', UserEmailResendConfirmation.as_view()),
    path('request-reset-password/', UserRequestPasswordReset.as_view()),
    path('reset-password/', UserPasswordReset.as_view()),
    path('request-username/', UserRequestUsername.as_view()),
    path('alerts/', Alerts.as_view()),
    path('webpush-save/', SaveWebPushInfo.as_view()),
]
