from django.urls import path
from .views import UserData, Groups, UserProfile, UserEmailConfirmation, UserEmailResendConfirmation, \
    UserRequestPasswordReset, UserPasswordReset, UserRequestUsername, \
    SaveWebPushInfoView, TokenObtainPairView, TokenRefreshView, AlertsView, UsersView, SaveUserView, Permissions, SecurityAuditView, Links

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #TokenRefreshView.as_view()
    path('user-data/', UserData.as_view()),
    #path('user-links/', UserLinksView.as_view()),
    path('groups/', Groups.as_view()),
    path('permissions/', Permissions.as_view()),
    path('profile/', UserProfile.as_view()),
    path('confirm/', UserEmailConfirmation.as_view()),
    path('confirm/resend/', UserEmailResendConfirmation.as_view()),
    path('request-reset-password/', UserRequestPasswordReset.as_view()),
    path('reset-password/', UserPasswordReset.as_view()),
    path('request-username/', UserRequestUsername.as_view()),
    path('alerts/', AlertsView.as_view()),
    path('webpush-save/', SaveWebPushInfoView.as_view()),
    path('users/', UsersView.as_view()),
    path('save/', SaveUserView.as_view()),
    path('security-audit/', SecurityAuditView.as_view()),
    path('links/', Links.as_view()),
]
