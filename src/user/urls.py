from django.urls import path
from .views import UserData, Groups, UserProfile, UserEmailConfirmation, UserEmailResendConfirmation, \
    UserRequestPasswordReset, UserPasswordReset, UserRequestUsername, \
    SaveWebPushInfoView, TokenObtainPairView, TokenRefreshView, AlertsView, UsersView, SaveUserView, Permissions, SecurityAuditView, Links

app_name = "user"

# Wire up our API using atomic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #TokenRefreshView.as_view()
    path('user-data/', UserData.as_view(), name="user-data"),
    #path('user-links/', UserLinksView.as_view()),
    path('groups/', Groups.as_view(), name="groups"),
    path('permissions/', Permissions.as_view(), name="permissions"),
    path('profile/', UserProfile.as_view(), name="profile"),
    path('confirm/', UserEmailConfirmation.as_view(), name="confirm"),
    path('confirm/resend/', UserEmailResendConfirmation.as_view(), name="confirm-resend"),
    path('request-reset-password/', UserRequestPasswordReset.as_view(), name="request-reset-password"),
    path('reset-password/', UserPasswordReset.as_view(), name="reset-password"),
    path('request-username/', UserRequestUsername.as_view(), name="request-username"),
    path('alerts/', AlertsView.as_view(), name="alerts"),
    path('webpush-save/', SaveWebPushInfoView.as_view(), name="webpush-save"),
    path('users/', UsersView.as_view(), name="users"),
    path('save/', SaveUserView.as_view(), name="save"),
    path('security-audit/', SecurityAuditView.as_view(), name="security-audit"),
    path('links/', Links.as_view(), name="links"),
]
