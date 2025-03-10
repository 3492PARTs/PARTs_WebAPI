from django.db import transaction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import sponsoring.util
from general.security import ret_message, has_access
from sponsoring.serializers import ItemSerializer, SponsorSerializer, ItemSponsorSerializer, SaveItemSerializer, \
    SaveSponsorOrderSerializer

auth_obj = 'scoutadmin'
app_url = 'sponsoring/'


class GetItems(APIView):
    """
    API endpoint to items
    """
    endpoint = 'get-items/'

    def get(self, request, format=None):
        try:
            items = sponsoring.util.get_items()
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting items.', True, app_url + self.endpoint,
                               request.user.id, e)


class GetSponsors(APIView):
    """
    API endpoint to get sponsors
    """
    endpoint = 'get-sponsors/'

    def get(self, request, format=None):
        try:
            sponsors = sponsoring.util.get_sponsors()
            serializer = SponsorSerializer(sponsors, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting sponsors.', True, app_url + self.endpoint,
                               request.user.id, e)


class SaveSponsor(APIView):
    """API endpoint to save a sponsor"""

    endpoint = 'save-sponsor/'

    def post(self, request, format=None):
        serializer = SponsorSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               error_message=serializer.errors)

        try:
            with transaction.atomic():
                sponsoring.util.save_sponsor(serializer.validated_data)
            return ret_message('Saved sponsor data successfully.')
        except Exception as e:
            return ret_message('An error occurred while saving sponsor data.', True,
                               app_url + self.endpoint, request.user.id, e)


class SaveItem(APIView):
    """
    API endpoint to save an item
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-item/'

    def post(self, request, format=None):
        serializer = SaveItemSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               error_message=serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                with transaction.atomic():
                    sponsoring.util.save_item(serializer.validated_data)
                return ret_message('Saved item data successfully.')
            except Exception as e:
                return ret_message('An error occurred while saving item data.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SaveSponsorOrder(APIView):
    """
    API endpoint to save a sponsor's order
    """
    endpoint = 'save-sponsor-order/'

    def post(self, request, format=None):
        serializer = SaveSponsorOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               error_message=serializer.errors)

        try:
            with transaction.atomic():
                sponsoring.util.save_sponsor_order(serializer.validated_data)
            return ret_message('Saved data successfully.')
        except Exception as e:
            return ret_message('An error occurred while saving data.', True,
                               app_url + self.endpoint, request.user.id, e)
