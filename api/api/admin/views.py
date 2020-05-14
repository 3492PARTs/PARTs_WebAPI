
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from api.api.serializers import *
from api.auth.serializers import PhoneTypeSerializer, ErrorLogSerializer
from rest_framework.views import APIView
from api.auth.security import *

auth_obj = 7


class GetInit(APIView):
    """
    API endpoint to get all the init values for the admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self):
        users = AuthUser.objects.filter(
            Q(is_active=True) & Q(date_joined__isnull=False))  # & ~Q(id=self.request.user.id))

        user_groups = AuthGroup.objects.all()

        phone_types = PhoneType.objects.all()

        return {'users': users, 'userGroups': user_groups, 'phoneTypes': phone_types}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init()
                serializer = AdminInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'GetAdminInit', request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, 'GetAdminInit', request.user.id)


class GetErrors(APIView):
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
                return ret_message('An error occurred while getting errors.', True, 'GetAdminErrors', request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, 'GetAdminErrors', request.user.id)
