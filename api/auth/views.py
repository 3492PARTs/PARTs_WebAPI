import ast
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django import forms
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordResetForm

from . import send_email
from .forms import SignupForm, ResendActivationEmailForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import *
from .security import *

from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
import secrets
from django.conf import settings
import pytz


def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            try:
                current_site = get_current_site(request)
                cntx = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
                mail_subject = 'Activate your PARTs account.'

                to_email = form.cleaned_data.get('email')

                send_email.send_message(
                    to_email, mail_subject, 'acc_active_email', cntx)
                return render(request, 'registration/register_complete.html')
            except Exception as e:
                print(e)
                ret_message(
                    'An error occurred while creating a user.', True, 'register', e)
                user.delete()
                return render(request, 'registration/register_fail.html')
    else:
        form = SignupForm()
    # TODO maybe check email here and yeah
    return render(request, 'registration/register.html', {'form': form})


def resend_activation_email(request):
    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'

    context = {}

    form = None
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data["email"]
            user = User.objects.get(email=to_email, is_active=0)
            current_site = get_current_site(request)
            cntx = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
            mail_subject = 'Activate your PARTs account.'

            send_email.send_message(
                to_email, mail_subject, 'acc_active_email', cntx)
            return render(request, 'registration/register_complete.html')

    if not form:
        form = ResendActivationEmailForm()

    context.update({"form": form})
    return render(request, 'registration/resend_activation_email_form.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return render(request, 'registration/activate_complete.html')
    else:
        return render(request, 'registration/activate_incomplete.html')


class GetUserData(APIView):
    """
    API endpoint
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_user(self):
        user = User.objects.select_related(
            'profile').get(id=self.request.user.id)

        return user

    def get(self, request, format=None):
        try:
            req = self.get_user()
            serializer = UserSerializer(req)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting user data.', True, 'auth/GetUserData',
                               request.user.id, e)


class GetUserLinks(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_links(self):
        permissions = get_user_permissions(self.request.user.id)

        user_links = UserLinks.objects.filter(
            permission__in=[per.id for per in permissions]).order_by('order')

        req = []

        for link in user_links:
            req.append({'MenuName': link.menu_name,
                        'RouterLink': link.routerlink})

        return req

    def get(self, request, format=None):
        try:
            req = self.get_links()
            serializer = UserLinksSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting user links.', True, 'auth/GetUserLinks',
                               request.user.id, e)


class GetUserGroups(APIView):
    """
    API endpoint to get groups a user has based on permissions
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_groups(self, user_id):
        return get_user_groups(user_id)

    def get(self, request, format=None):
        try:
            req = self.get_groups(request.query_params.get('user_id', None))
            serializer = GroupSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting user groups.', True, 'auth/GetUserGroups',
                               request.user.id, e)


class GetAPIStatus(APIView):
    """
    API endpoint to get if the api is available
    """

    def get(self, request, format=None):
        return Response(200)


class HTMLPasswordResetForm(PasswordResetForm):
    """
    Override the password reset form to send html emails
    """
    email = forms.EmailField(label=("Email"), max_length=254)

    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html', use_https=False,
             token_generator=default_token_generator, from_email=None, request=None, **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        :param from_email:
        :param request:
        :param use_https:
        :param domain_override:
        :param subject_template_name:
        :param token_generator:
        :param email_template_name:
        :param **kwargs:
        :param **kwargs:
        """
        email = self.cleaned_data["email"]
        user = User.objects.get(
            email__iexact=email, is_active=True)

        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        c = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }
        send_email.send_message(
            email, 'PARTs Password Reset', 'password_reset_email', c)


# New user management
class UserProfileView(APIView):
    """
    Handles registering new users and management of user profiles.
    """
    #queryset = UserProfile.objects.all().order_by('-id')
    #permission_classes = [UserPermission]
    #serializer_class = UserProfileSerializer
    #parser_classes = [JSONParser, FormParser, MultiPartParser]

    def put(self, request):
        try:
            serialized = UserCreationSerializer(data=request.data)
            if serialized.is_valid():
                #user_confirm_hash = abs(hash(serialized.data.date_joined))
                if serialized.data.get('password1', 't') != serialized.data.get('password2', 'y'):
                    return ret_message('Passwords don\'t match.', True, 'auth/profile', 0)

                user_data = serialized.validated_data
                user = User(username=user_data.get('username'), email=user_data.get('email'), first_name=user_data.get('first_name'),
                            last_name=user_data.get('last_name'), date_joined=timezone.now())

                #user = form.save(commit=False)
                user.is_active = False
                user.set_password(user_data.get('password1'))
                user.save()

                current_site = get_current_site(request)

                user_confirm_hash = abs(hash(user.date_joined))

                cntx = {
                    'user': user,
                    'url': request.scheme + '://' + current_site.domain + '/auth/confirm/?pk={}&confirm={}'.format(user.username, user_confirm_hash)
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
                return ret_message('An error occurred while creating user.' + error_str, True, 'auth/profile',
                                   0, serialized._errors)
        except Exception as e:
            error_string = str(e)
            if error_string == 'UNIQUE constraint failed: auth_user.username':
                error_string = 'A user with that username already exists.'
            else:
                error_string = None
            return ret_message('An error occurred while creating user.' + ('\n' + error_string if error_string is not None else None), True, 'auth/profile', exception=e)

    # TODO Add auth
    def update(self, request, pk=None):
        user = self.queryset.filter(id=pk).first()
        if user is None:
            return ret_message('An error occurred while updating user data.', True, 'auth/profile',
                               0)
        self.check_object_permissions(request, user)
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        # flag used to email user the user's old email about the change in the event that both the email and password are updated
        password_changed = False
        if serializer.is_valid():
            if "password" in serializer.validated_data:
                try:
                    validate_password(
                        serializer.validated_data["password"], user=request.user, password_validators=get_default_password_validators())
                except ValidationError as e:
                    return ret_message('An error occurred changing password.', True, 'auth/user',
                                       request.user.id, e)
                password_changed = True
                user.set_password(serializer.validated_data["password"])
                cntx = {'user': user,
                        'message': 'Your password has been updated. If you did not do this, please secure your account by requesting a password reset as soon as possible.'}

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
                        'message': 'Your email has been updated to "{}", if you did not do this, please secure your account by changing your password as soon as possible.'.format(user.email)}
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
                            'message': 'Your password has been updated. If you did not do this, please secure your account by requesting a password reset as soon as possible.'}
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
                user.image = serializer.validated_data["image"]
            if request.user.is_superuser:  # only allow role editing if admin
                if "is_staff" in serializer.validated_data:
                    user.is_staff = serializer.validated_data["is_staff"]
                if "is_active" in serializer.validated_data:
                    user.is_active = serializer.validated_data["is_active"]
                if "is_superuser" in serializer.validated_data:
                    user.is_superuser = serializer.validated_data["is_superuser"]
            user.save()
            serializer = UserProfileSerializer(instance=user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return ret_message('An error occurred while updating user data.', True, 'auth/user',
                               user.id, serializer.errors)

    # there should be no path to this, but leave it here just in case
    """
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
    def get(self, request):
        try:
            req = self.confirm_email(request)
            return req
        except Exception as e:
            return ret_message('Failed to activate user\'s account.', True,
                               'auth/activate', exception=e)

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
                ret_message('An error occurred while confirming the user\'s account.', True, 'auth/activate',
                            user.id)
                return redirect(settings.FRONTEND_ADDRESS + "/login?page=activationFail")
        except ObjectDoesNotExist as o:
            ret_message(
                'An error occurred while confirming the user\'s account.', True, 'auth/activate', o)
            return redirect(settings.FRONTEND_ADDRESS + "/login?page=activationFail")


class UserEmailResendConfirmation(APIView):
    def post(self, request):
        try:
            req = self.resend_confirmation_email(request)
            return req
        except Exception as e:
            return ret_message('Failed to resend user confirmation email.', True,
                               'auth/confirm/resend/', exception=e)

    def resend_confirmation_email(self, request):
        user = User.objects.get(email=request.data['email'])
        current_site = get_current_site(request)

        user_confirm_hash = abs(hash(user.date_joined))

        cntx = {
            'user': user,
            'url': request.scheme + '://' + current_site.domain + '/auth/confirm/?pk={}&confirm={}'.format(user.username, user_confirm_hash)
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
    def post(self, request):
        try:
            req = self.request_reset_password(request)
            return req
        except Exception as e:
            return ret_message('Failed to request password reset.', True,
                               'auth/request_reset_password', exception=e)

    def request_reset_password(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:  # if the user has confirmed their email
                user.reset_token = secrets.token_urlsafe(24)
                user.reset_requested_at = timezone.now()
                user.save()

                current_site = get_current_site(request)
                cntx = {
                    'user': user,
                    'url': settings.FRONTEND_ADDRESS + 'login/?page=resetConfirm&user={}&confirm={}'.format(
                        user.username, user.reset_token)
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
                        'auth/profile/request_reset_password', exception=e)
        # regardless if we find a user or not, send back the same info. Prevents probing for user emails.
        return ret_message('If a matching user was found you will receive an email shortly.')


class UserPasswordReset(APIView):
    def post(self, request):
        try:
            req = self.reset_password(request)
            return req
        except Exception as e:
            return ret_message('Failed to reset password.', True,
                               'auth/reset_password', exception=e)

    def reset_password(self, request):
        try:
            username = request.data['username']
            confirm = request.data['confirm']
            password = request.data['password']

            user = User.objects.filter(username=username)[0]
            if confirm == None:  # prevents
                return ret_message('Reset token required.', True, 'auth/reset_password', exception=request.data['email'])
            if (confirm == user.reset_token) and ((user.reset_requested_at + timedelta(hours=1)) > timezone.now()):
                try:
                    validate_password(password, UserProfile.objects.get(
                        username=username), password_validators=get_default_password_validators())
                except ValidationError as e:
                    return ret_message('Password invalid' + str(e), True, 'auth/reset_password', user.id, e)
                user.reset_token = None  # wipe the token so it can't be used twice
                user.set_password(password)
                user.save()
                return ret_message('Password updated successfully.')
            else:
                return ret_message('Invalid token or request timed out.', True, 'auth/reset_password', user.id)
        except KeyError as e:
            e = str(e)
            e = e.strip("'")
            return ret_message(e + " missing from request but is required", True, 'auth/reset_password', exception=e)
