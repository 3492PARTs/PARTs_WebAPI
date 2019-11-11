from django.core import signing
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.template import Context

from api import settings
from .forms import SignupForm, ResendActivationEmailForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from api.auth.serializers import UserSerializer
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response


def register(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # TODO on error delete user
            user.save()

            try:
                current_site = get_current_site(request)
                mail_subject = 'Activate your flood account.'
                message = render_to_string('email_templates/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                            mail_subject, message, to=[to_email]
                )
                email.send()
                return render(request, 'registration/register_complete.html')
            except Exception:
                user.delete()
                return render(request, 'registration/register_fail.html')
    else:
        form = SignupForm()
    return render(request, 'registration/register.html', {'form': form}) #TODO maybe check email here and yeah


def resend_activation_email(request):

    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'

    context = {}

    form = None
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email, is_active=0)
            current_site = get_current_site(request)
            mail_subject = 'Activate your flood account.'
            message = render_to_string('email_templates/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/register_complete.html')

    if not form:
        form = ResendActivationEmailForm()

    context.update({"form" : form})
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


# Custom permission for users with "is_active" = True.
class scoutupdate(BasePermission):
    """
    Allows access only to "is_active" users.
    """
    def has_permission(self, request, view):
        print(request.user.user_permissions)
        return request.user


class UserData(APIView):
    """
    API endpoint
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, scoutupdate)

    def get_user(self, token):
        user = AuthtokenToken.objects.get(key=token['token']).user

        return user

    def post(self, request, format=None):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            req = self.get_user(serializer.data)
            serializer = UserSerializer(req)
            return Response(serializer.data)
        return HttpResponse(status=400)

class UserLinks(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_links(self, req):


        return req

    def post(self, request, format=None):
        serializer = MainQuerySerializer(data=request.data)
        if serializer.is_valid():
            req = self.generate_data(serializer.data)
            serializer = MainQuerySerializer(req)
            return Response(serializer.data)
        return HttpResponse(status=400)