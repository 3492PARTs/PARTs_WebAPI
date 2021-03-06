from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.forms import PasswordResetForm

from api import settings
from . import send_email
from .forms import SignupForm, ResendActivationEmailForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string, get_template
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from .security import *


def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # TODO on error delete user
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

                send_email.send_message(to_email, mail_subject, 'acc_active_email', cntx)
                return render(request, 'registration/register_complete.html')
            except Exception as e:
                print(e)
                # TODO ret_message('An error occurred while creating a user.', True, 'register', e)
                user.delete()
                return render(request, 'registration/register_fail.html')
    else:
        form = SignupForm()
    return render(request, 'registration/register.html', {'form': form})  # TODO maybe check email here and yeah


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

            send_email.send_message(to_email, mail_subject, 'acc_active_email', cntx)
            return render(request, 'registration/register_complete.html')

    if not form:
        form = ResendActivationEmailForm()

    context.update({"form": form})
    return render(request, 'registration/resend_activation_email_form.html', context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_user(self):
        user = User.objects.select_related('profile').get(id=self.request.user.id)

        return user

    def get(self, request, format=None):
        req = self.get_user()
        serializer = UserSerializer(req)
        return Response(serializer.data)


class GetUserLinks(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_links(self):
        permissions = get_user_permissions(self.request.user.id)

        user_links = UserLinks.objects.filter(
            permission__in=[per.id for per in permissions]).order_by('order')

        req = []

        for link in user_links:
            req.append({'MenuName': link.menu_name, 'RouterLink': link.routerlink})

        return req

    def get(self, request, format=None):
        req = self.get_links()
        serializer = UserLinksSerializer(req, many=True)
        return Response(serializer.data)


class GetUserGroups(APIView):
    """
    API endpoint to get groups a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_groups(self, user_id):
        return get_user_groups(user_id)

    def get(self, request, format=None):
        req = self.get_groups(request.query_params.get('user_id', None))
        serializer = GroupSerializer(req, many=True)
        return Response(serializer.data)


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
        send_email.send_message(email, 'PARTs Password Reset', 'password_reset_email', c)
