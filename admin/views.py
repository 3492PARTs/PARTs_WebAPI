from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from user.models import PhoneType
from .serializers import ErrorLogSerializer, InitSerializer, SaveUserSerializer
from .models import ErrorLog
from rest_framework.views import APIView
from general.security import has_access, ret_message
from django.contrib.auth.models import Group
from django.db.models.functions import Lower
from rest_framework.response import Response
from django.db.models import Q
from user.models import User

auth_obj = 55
auth_obj_save_user = 56
app_url = 'admin/'


class Init(APIView):
    """
    API endpoint to get all the init values for the admin screen
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'init/'

    def init(self):
        users = User.objects.filter(
            Q(date_joined__isnull=False)).order_by(Lower('first_name'), Lower('last_name'))

        user_groups = Group.objects.all().order_by('name')

        phone_types = PhoneType.objects.all().order_by('carrier')

        return {'users': users, 'userGroups': user_groups, 'phoneTypes': phone_types}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.init()
                serializer = InitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint, request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SaveUser(APIView):
    """API endpoint to save user data"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-user/'

    def save_user(self, data):
        try:
            groups = []
            user = User.objects.get(username=data['user']['username'])
            user.first_name = data['user']['first_name']
            user.last_name = data['user']['last_name']
            user.email = data['user']['email'].lower()
            user.discord_user_id = data['user']['discord_user_id']
            user.phone = data['user']['phone']
            user.phone_type_id = data['user'].get('phone_type_id', None)
            user.is_active = data['user']['is_active']
            user.save()

            for d in data['groups']:
                groups.append(d['name'])
                aug = user.groups.filter(name=d['name']).exists()
                if not aug:
                    group = Group.objects.get(name=d['name'])
                    user.groups.add(group)

            user_groups = user.groups.all()
            user_groups = user_groups.filter(~Q(name__in=groups))

            for user_group in user_groups:
                user_group.user_set.remove(user)

            return ret_message('Saved user successfully')
        except Exception as e:
            return ret_message('Can\'t save the user', True, app_url + self.endpoint, self.request.user.id, e)

    def post(self, request, format=None):
        serializer = SaveUserSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj_save_user):
            try:
                req = self.save_user(serializer.validated_data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the user.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class ErrorLogView(APIView):
    """
    API endpoint to get errors for the admin screen
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'error-log/'

    def get_errors(self, pg):
        errors = ErrorLog.objects.filter(void_ind='n').order_by('-time')
        paginator = Paginator(errors, 10)
        try:
            errors = paginator.page(pg)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            errors = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999),
            # deliver last page of results.
            errors = paginator.page(paginator.num_pages)

        previous_pg = None if not errors.has_previous() else errors.previous_page_number()
        next_pg = None if not errors.has_next() else errors.next_page_number()
        serializer = ErrorLogSerializer(errors, many=True)
        data = {'count': paginator.num_pages, 'previous': previous_pg,
                'next': next_pg, 'errors': serializer.data}
        return data

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_errors(request.query_params.get('pg_num', 1))
                return Response(req)
            except Exception as e:
                return ret_message('An error occurred while getting errors.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)
