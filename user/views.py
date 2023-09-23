import ast
import datetime

import cloudinary
import webpush.views
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from pytz import timezone, utc
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from webpush import send_user_notification

import alerts.util
import user.util
from api.settings import AUTH_PASSWORD_VALIDATORS
from .serializers import GroupSerializer, UserCreationSerializer, UserLinksSerializer, UserSerializer, \
    UserUpdateSerializer, GetAlertsSerializer, SaveUserSerializer
from .models import User, UserLinks
from general.security import get_user_groups, get_user_permissions, ret_message, has_access

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
import secrets
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt import views as jwt_views

auth_obj_save_user = 56
app_url = 'user/'


class TokenObtainPairView(APIView):
    """
    API endpoint to get a  user token
    """
    endpoint = 'token/'

    def post(self, request, format=None):
        try:
            serializer = TokenObtainPairSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message('Invalid data', True, app_url + self.endpoint, 0, serializer.errors)

            return Response(serializer.validated_data)
        except Exception as e:
            return ret_message('An error occurred while logging in.', True,
                               app_url + self.endpoint,
                               0, e)


class TokenRefreshView(APIView):
    """
    API endpoint to get a  user token
    """
    endpoint = 'token/refresh/'

    def post(self, request, format=None):
        try:
            serializer = TokenRefreshSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message('Invalid data', True, app_url + self.endpoint, 0, serializer.errors)

            return Response(serializer.validated_data)
        except Exception as e:
            return ret_message('An error occurred while refreshing token.', True,
                               app_url + self.endpoint,
                               0, e)


class UserLogIn(ModelBackend):
    def authenticate(self, request, **kwargs):
        UserModel = get_user_model()
        try:
            username = kwargs.get('username', None)
            user = UserModel.objects.get((Q(email=username) | Q(username=username)) & Q(is_active=True))
            if user.check_password(kwargs.get('password', None)):
                return user
        except UserModel.DoesNotExist:
            return None
        return None


class UserProfile(APIView):
    """
    Handles registering new users and management of user profiles.
    """
    endpoint = 'profile/'

    def post(self, request):
        try:
            serialized = UserCreationSerializer(data=request.data)
            if serialized.is_valid():
                # user_confirm_hash = abs(hash(serialized.data.date_joined))
                if serialized.data.get('password1', 't') != serialized.data.get('password2', 'y'):
                    return ret_message('Passwords don\'t match.', True, app_url + self.endpoint, 0)

                user_data = serialized.validated_data

                try:
                    user = User.objects.get(
                        email=user_data.get('email').lower())
                    return ret_message('User already exists with that email.', True, app_url + self.endpoint, 0,
                                       user_data.get('email').lower())
                except ObjectDoesNotExist as odne:
                    x = 0

                user = User(username=user_data.get('username').lower(), email=user_data.get('email').lower(),
                            first_name=user_data.get('first_name'),
                            last_name=user_data.get('last_name'),
                            date_joined=datetime.datetime.utcnow().replace(tzinfo=utc))

                # user = form.save(commit=False)
                user.is_active = False
                user.set_password(user_data.get('password1'))
                user.save()

                current_site = get_current_site(request)

                user_confirm_hash = abs(hash(user.date_joined))

                cntx = {
                    'user': user,
                    'url': request.scheme + '://' + current_site.domain + '/user/confirm/?pk={}&confirm={}'.format(
                        user.username, user_confirm_hash)
                }

                send_mail(
                    subject="Activate your PARTs account.",
                    message=render_to_string(
                        "email_templates/acc_active_email.txt", cntx).strip(),
                    html_message=render_to_string(
                        "email_templates/acc_active_email.html", cntx).strip(),
                    from_email="team3492@gmail.com",
                    recipient_list=[user.email]
                )

                return ret_message('User created')
            else:
                ed = serialized._errors.get('password1').get('password')
                error_list = ast.literal_eval(ed.title())
                error_str = ''
                for e in error_list:
                    error_str += '\n' + e
                return ret_message('An error occurred while creating user.' + error_str, True, app_url + self.endpoint,
                                   0, serialized._errors)
        except Exception as e:
            error_string = str(e)
            if error_string == 'UNIQUE constraint failed: auth_user.username':
                error_string = 'A user with that username already exists.'
            else:
                error_string = None
            return ret_message(
                'An error occurred while creating user.' + ('\n' + error_string if error_string is not None else ''),
                True, app_url + self.endpoint, exception=e)

    def put(self, request, pk=None):
        try:
            user = User.objects.get(id=self.request.user.id)
            if user.is_authenticated:
                if user is None:
                    return ret_message('An error occurred while updating user data.', True, app_url + self.endpoint,
                                       0)
                serializer = UserUpdateSerializer(data=request.data)
                # flag used to email user the user's old email about the change in the event that both the email and
                # password are updated
                password_changed = False
                if serializer.is_valid():
                    if "password" in serializer.validated_data:
                        try:
                            validate_password(
                                serializer.validated_data["password"], user=request.user,
                                password_validators=get_default_password_validators())
                        except ValidationError as e:
                            return ret_message('An error occurred changing password.', True, app_url + self.endpoint,
                                               request.user.id, e)
                        password_changed = True
                        user.set_password(serializer.validated_data["password"])
                        cntx = {'user': user,
                                'message': 'Your password has been updated. If you did not do this, please secure your '
                                           'account by requesting a password reset as soon as possible.'}

                        send_mail(
                            subject="Password Change",
                            message=render_to_string(
                                'email_templates/generic_email.txt', cntx).strip(),
                            html_message=render_to_string(
                                'email_templates/generic_email.html', cntx).strip(),
                            from_email='team3492@gmail.com',
                            recipient_list=[user.email]
                        )
                    if "email" in serializer.validated_data and user.email != serializer.validated_data["email"]:
                        old_email = user.email
                        user.email = serializer.validated_data["email"]
                        user.save()  # checks for db violations, unique constraints and such
                        cntx = {'user': user,
                                'message': 'Your email has been updated to "{}", if you did not do this, please secure '
                                           'your account by changing your password as soon as possible.'.format(
                                    user.email)}
                        send_mail(
                            subject="Email Updated",
                            message=render_to_string(
                                'email_templates/generic_email.txt', cntx).strip(),
                            html_message=render_to_string(
                                'email_templates/generic_email.html', cntx).strip(),
                            from_email='team3492@gmail.com',
                            recipient_list=[user.email, old_email]
                        )
                        if password_changed:
                            cntx = {'user': user,
                                    'message': 'Your password has been updated. If you did not do this, please secure '
                                               'your account by requesting a password reset as soon as possible.'}
                            send_mail(
                                subject="Password Changed",
                                message=render_to_string(
                                    'email_templates/generic_email.txt', cntx).strip(),
                                html_message=render_to_string(
                                    'email_templates/generic_email.html', cntx).strip(),
                                from_email='team3492@gmail.com',
                                recipient_list=[user.email]
                            )
                    if "first_name" in serializer.validated_data:
                        user.first_name = serializer.validated_data["first_name"]
                    if "last_name" in serializer.validated_data:
                        user.last_name = serializer.validated_data["last_name"]
                    if "image" in serializer.validated_data:
                        if user.img_id:
                            response = cloudinary.uploader.upload(serializer.validated_data["image"],
                                                                  public_id=user.img_id)
                        else:
                            response = cloudinary.uploader.upload(serializer.validated_data["image"])
                        user.img_id = response['public_id']
                        user.img_ver = str(response['version'])
                    if request.user.is_superuser:  # only allow role editing if admin
                        if "is_staff" in serializer.validated_data:
                            user.is_staff = serializer.validated_data["is_staff"]
                        if "is_active" in serializer.validated_data:
                            user.is_active = serializer.validated_data["is_active"]
                        if "is_superuser" in serializer.validated_data:
                            user.is_superuser = serializer.validated_data["is_superuser"]
                    user.save()
                    return ret_message('Successfully updated user info.')
                else:
                    return ret_message('An error occurred while updating user data.', True, app_url + self.endpoint,
                                       user.id, serializer.errors)
            else:
                return ret_message('Not authenticated.', True, app_url + self.endpoint)
        except Exception as e:
            error_string = str(e)
            if error_string == 'UNIQUE constraint failed: auth_user.username':
                error_string = 'A user with that username already exists.'
            else:
                error_string = None
            return ret_message(
                'An error occurred while updating user.' + ('\n' + error_string if error_string is not None else ''),
                True, app_url + self.endpoint, exception=e)

    """
    # there should be no path to this, but leave it here just in case
    
    def partial_update(self, request, pk=None):
        message = ResponseMessage("Not implemented", rep_status.success)
        return Response(data=message.jsonify(), status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        self.check_object_permissions(request, self.queryset.get(id=pk))
        message = ResponseMessage("Not implemented", rep_status.success)
        # TODO work out later
        return Response(data=message.jsonify(), status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        pk = int(pk)
        self.check_object_permissions(request, self.queryset.get(id=pk))
        if request.user.is_superuser and (request.user.id != pk):
            # don't show admins the user's secrets.
            serializer = UserProfileSerializer
        else:
            serializer = CompleteUserProfileSerializer
        profile = self.queryset.get(id=pk)
        if profile is not None:
            serialized = serializer(instance=profile)
            return Response(data=serialized.data, status=status.HTTP_200_OK)
        else:
            return Response(ResponseMessage("User does not exist", rep_status.not_found).jsonify(), status=status.HTTP_404_NOT_FOUND)
    """


class UserEmailConfirmation(APIView):
    endpoint = 'confirm/'

    def get(self, request):
        try:
            req = self.confirm_email(request)
            return req
        except Exception as e:
            return ret_message('Failed to activate user\'s account.', True,
                               app_url + self.endpoint, exception=e)

    def confirm_email(self, request, pk=None):
        """
        Confirms the user's email by checking the user provided hash with the server calculated one. Allows user to login if 
        successful.
        """
        try:
            user = User.objects.get(username=request.GET.get('pk'))
            user_confirm_hash = abs(hash(user.date_joined))

            if int(request.GET.get('confirm')) == user_confirm_hash:
                user.is_active = True
                user.save()
                return redirect(settings.FRONTEND_ADDRESS + "/login?page=activationConfirm")
            else:
                ret_message('An error occurred while confirming the user\'s account.', True, app_url + self.endpoint,
                            user.id)
                return redirect(settings.FRONTEND_ADDRESS + "/login?page=activationFail")
        except ObjectDoesNotExist as o:
            ret_message(
                'An error occurred while confirming the user\'s account.', True, app_url + self.endpoint, 0, o)
            return redirect(settings.FRONTEND_ADDRESS + "/login?page=activationFail")


class UserEmailResendConfirmation(APIView):
    endpoint = 'confirm/resend/'

    def post(self, request):
        try:
            req = self.resend_confirmation_email(request)
            return req
        except Exception as e:
            return ret_message('Failed to resend user confirmation email.', True,
                               app_url + self.endpoint, exception=e)

    def resend_confirmation_email(self, request):
        user = User.objects.get(email=request.data['email'].lower())
        current_site = get_current_site(request)

        user_confirm_hash = abs(hash(user.date_joined))

        cntx = {
            'user': user,
            'url': request.scheme + '://' + current_site.domain + '/user/confirm/?pk={}&confirm={}'.format(
                user.username, user_confirm_hash)
        }

        send_mail(
            subject="Activate your PARTs account.",
            message=render_to_string(
                "email_templates/acc_active_email.txt", cntx).strip(),
            html_message=render_to_string(
                "email_templates/acc_active_email.html", cntx).strip(),
            from_email="team3492@gmail.com",
            recipient_list=[user.email]
        )
        return ret_message('If a matching user was found you will receive an email shortly.')


class UserRequestPasswordReset(APIView):
    endpoint = 'request-reset-password/'

    def post(self, request):
        try:
            req = self.request_reset_password(request)
            return req
        except Exception as e:
            return ret_message('Failed to request password reset.', True,
                               app_url + self.endpoint, exception=e)

    def request_reset_password(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email.lower())
            if user.is_active:  # if the user has confirmed their email
                user.reset_token = secrets.token_urlsafe(24)
                user.reset_requested_at = datetime.datetime.utcnow().replace(tzinfo=utc)
                user.save()

                cntx = {
                    'user': user,
                    'url': settings.FRONTEND_ADDRESS + 'login/?page=resetConfirm&uuid={}&token={}'.format(
                        urlsafe_base64_encode(force_bytes(user.pk)), default_token_generator.make_token(user))
                }

            send_mail(
                subject="Password Reset Requested",
                message=render_to_string(
                    "email_templates/password_reset_email.txt", cntx).strip(),
                html_message=render_to_string(
                    "email_templates/password_reset_email.html", cntx).strip(),
                from_email="team3492@gmail.com",
                recipient_list=[user.email]
            )
        except Exception as e:
            ret_message('Failed user reset attempt', True,
                        app_url + self.endpoint, exception=e)
        # regardless if we find a user or not, send back the same info. Prevents probing for user emails.
        return ret_message('If a matching user was found you will receive an email shortly.')


class UserPasswordReset(APIView):
    endpoint = 'reset-password/'

    def post(self, request):
        try:
            req = self.reset_password(request)
            return req
        except Exception as e:
            return ret_message('Failed to reset password.', True,
                               app_url + self.endpoint, exception=e)

    def reset_password(self, request):
        try:
            # username = request.data['username']
            uuid = request.data['uuid']
            token = request.data['token']
            password = request.data['password']

            user_id = urlsafe_base64_decode(uuid)

            user = User.objects.get(id=user_id)
            if token == None or uuid == None:  # prevents
                return ret_message('Reset token required.', True, app_url + self.endpoint,
                                   exception=request.data['email'])
            # TODO Add time component back and ((user.reset_requested_at + timedelta(hours=1)) > timezone.now()):
            if (default_token_generator.check_token(user, token)):
                try:
                    validate_password(
                        password, user)
                except ValidationError as e:
                    return ret_message('Password invalid' + str(e), True, app_url + self.endpoint, user.id, e)
                user.set_password(password)
                user.save()
                return ret_message('Password updated successfully.')
            else:
                return ret_message('Invalid token or request timed out.', True, app_url + self.endpoint, user.id)
        except KeyError as e:
            e = str(e)
            e = e.strip("'")
            return ret_message(e + " missing from request but is required", True, app_url + self.endpoint, exception=e)


class UserRequestUsername(APIView):
    endpoint = 'request-username/'

    def post(self, request):
        try:
            req = self.forgot_username(request)
            return req
        except Exception as e:
            return ret_message('Failed to request username.', True,
                               app_url + self.endpoint, exception=e)

    def forgot_username(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email.lower())
            if user.is_active:  # if the user has confirmed their email

                cntx = {
                    'user': user
                }

            send_mail(
                subject="Username Requested",
                message=render_to_string(
                    "email_templates/forgot_username.txt", cntx).strip(),
                html_message=render_to_string(
                    "email_templates/forgot_username.html", cntx).strip(),
                from_email="team3492@gmail.com",
                recipient_list=[user.email]
            )
        except Exception as e:
            ret_message('Failed to request username.', True,
                        app_url + self.endpoint, exception=e)
        # regardless if we find a user or not, send back the same info. Prevents probing for user emails.
        return ret_message('If a matching user was found you will receive an email shortly.')


class UserData(APIView):
    """
    API endpoint
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'user-data/'

    def get_user(self):
        user = User.objects.get(id=self.request.user.id)

        user = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.first_name + ' ' + user.last_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'phone': user.phone,
            'groups': user.groups,
            'phone_type': user.phone_type,
            'phone_type_id': user.phone_type_id,
            'image': cloudinary.CloudinaryImage(user.img_id, version=user.img_ver).build_url()
        }

        return user

    def get(self, request, format=None):
        try:
            req = self.get_user()
            serializer = UserSerializer(req)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting user data.', True, app_url + self.endpoint,
                               request.user.id, e)


class UserLinksView(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'user-links/'

    def get_links(self):
        permissions = get_user_permissions(self.request.user.id)

        user_links = UserLinks.objects.filter(
            permission__in=[per.id for per in permissions]).order_by('order')

        return user_links

    def get(self, request, format=None):
        try:
            req = self.get_links()
            serializer = UserLinksSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting user links.', True, app_url + self.endpoint,
                               request.user.id, e)


class UserGroups(APIView):
    """
    API endpoint to get groups a user has based on permissions
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'user-groups/'

    def get_groups(self, user_id):
        return get_user_groups(user_id)

    def get(self, request, format=None):
        try:
            req = self.get_groups(request.query_params.get('user_id', None))
            serializer = GroupSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting user groups.', True, app_url + self.endpoint,
                               request.user.id, e)


class Alerts(APIView):
    """
    API endpoint to get a user's notifications
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'get-notifications/'

    def get(self, request, format=None):
        try:
            req = alerts.util.get_user_alerts(request.user.id, request.query_params.get('alert_comm_typ_id', None))
            serializer = GetAlertsSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting user alerts.', True, app_url + self.endpoint,
                               request.user.id, e)


class SaveWebPushInfo(APIView):
    """
    API endpoint to save a user push notification subscription object
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'webpush-save/'

    def post(self, request, format=None):
        try:
            response = webpush.views.save_info(request)
            if response.status_code == 400:
                return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, response)

            return ret_message('Successfully subscribed to push notifications.')
        except Exception as e:
            return ret_message('An error occurred while subscribing to push notifications.', True,
                               app_url + self.endpoint,
                               request.user.id, e)


class Users(APIView):
    """
    API endpoint to get users
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'users/'

    def get(self, request, format=None):
        try:
            req = user.util.get_users(int(request.query_params.get('is_active', '0')))
            serializer = UserSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting users.', True, app_url + self.endpoint,
                               request.user.id, e)


class SaveUser(APIView):
    """API endpoint to save user data"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save/'

    def post(self, request, format=None):
        serializer = SaveUserSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj_save_user):
            try:
                with transaction.atomic():
                    user.util.save_user(serializer.validated_data)
                    return ret_message('Saved user successfully')
            except Exception as e:
                return ret_message('An error occurred while saving the user.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)
