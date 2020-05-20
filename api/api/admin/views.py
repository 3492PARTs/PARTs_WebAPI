
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .serializers import *
from api.auth.serializers import PhoneTypeSerializer, ErrorLogSerializer
from rest_framework.views import APIView
from api.auth.security import *
from django.contrib.auth.models import User, Group

auth_obj = 7
auth_obj_save_user = 8


class GetInit(APIView):
    """
    API endpoint to get all the init values for the admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self):
        users = User.objects.select_related('profile').filter(
            Q(is_active=True) & Q(date_joined__isnull=False))  # & ~Q(id=self.request.user.id))

        user_groups = Group.objects.all()

        phone_types = PhoneType.objects.all()

        return {'users': users, 'userGroups': user_groups, 'phoneTypes': phone_types}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init()
                serializer = InitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'api/admin/GetInit', request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, 'api/admin/GetInit', request.user.id)


class PostSaveUser(APIView):
    """API endpoint to save user data"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_user(self, data):
        try:
            groups = []
            user = User.objects.get(username=data['user']['username'])
            user.first_name = data['user']['first_name']
            user.last_name = data['user']['last_name']
            user.profile.phone = data['user']['profile']['phone']
            user.profile.phone_type_id = data['user']['profile']['phone_type']
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
            return ret_message('Can\'t save the user', True, 'api/admin/PostSaveUser', self.request.user.id, e)

    def post(self, request, format=None):
        serializer = SaveUserSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'api/admin/PostSaveUser', request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj_save_user):
            try:
                req = self.save_user(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the user.', True, 'api/admin/PostSaveUser',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'api/admin/PostSaveUser', request.user.id)


class GetErrorLog(APIView):
    """
    API endpoint to get errors for the admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

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
                return ret_message('An error occurred while getting errors.', True, 'api/admin/GetErrorLog',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'api/admin/GetErrorLog', request.user.id)
