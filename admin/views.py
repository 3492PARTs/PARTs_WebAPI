from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import user.util
from user.models import PhoneType
from .serializers import ErrorLogSerializer, InitSerializer
from .models import ErrorLog
from rest_framework.views import APIView
from general.security import has_access, ret_message
from django.contrib.auth.models import Group
from rest_framework.response import Response

auth_obj = 55
app_url = 'admin/'


class Init(APIView):
    """
    API endpoint to get all the init values for the admin screen
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'init/'

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                user_groups = user.util.get_all_user_groups()
                phone_types = user.util.get_phone_types()
                req = {'userGroups': user_groups, 'phoneTypes': phone_types}
                serializer = InitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint, request.user.id,
                                   e)
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
