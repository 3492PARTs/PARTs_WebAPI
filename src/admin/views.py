from django.db import transaction
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import user.util
from scouting.models import ScoutAuthGroup
from user.models import PhoneType
from .serializers import (
    ErrorLogSerializer,
    GroupSerializer,
    PhoneTypeSerializer,
)
from .models import ErrorLog
from rest_framework.views import APIView
from general.security import has_access, ret_message
from rest_framework.response import Response

auth_obj = "admin"
app_url = "admin/"


class ErrorLogView(APIView):
    """
    API endpoint to get errors for the admin screen
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "error-log/"

    def get_errors(self, pg):
        errors = ErrorLog.objects.filter(void_ind="n").order_by("-time")
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

        previous_pg = (
            None if not errors.has_previous() else errors.previous_page_number()
        )
        next_pg = None if not errors.has_next() else errors.next_page_number()
        serializer = ErrorLogSerializer(errors, many=True)
        data = {
            "count": paginator.num_pages,
            "previous": previous_pg,
            "next": next_pg,
            "errors": serializer.data,
        }
        return data

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_errors(request.query_params.get("pg_num", 1))
                return Response(req)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting errors.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class ScoutAuthGroupsView(APIView):
    """
    API endpoint to manage the auth groups the scout admin can assign
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "scout-auth-groups/"

    def get(self, request, format=None):
        try:
            groups = user.util.get_groups().filter(
                id__in=list(
                    ScoutAuthGroup.objects.all().values_list("group_id", flat=True)
                )
            )
            serializer = GroupSerializer(groups, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message(
                "An error occurred while getting scout auth groups.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

    def post(self, request, format=None):
        serializer = GroupSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                error_message=serializer.errors,
            )

        if has_access(request.user.id, "admin"):
            try:
                with transaction.atomic():
                    keep = []
                    for s in serializer.validated_data:
                        keep.append(s["id"])
                        try:
                            ScoutAuthGroup.objects.get(group_id=s["id"])
                        except ScoutAuthGroup.DoesNotExist:
                            sag = ScoutAuthGroup(group_id=s["id"])
                            sag.save()

                    sags = ScoutAuthGroup.objects.filter(~Q(group_id__in=keep))
                    for s in sags:
                        s.delete()

                    return ret_message("Saved scout auth groups successfully")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the scout auth groups.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )


class PhoneTypeView(APIView):
    """
    API endpoint to get all phone types
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "phone-type/"

    def get(self, request, format=None):
        if has_access(request.user.id, [auth_obj, "scoutadmin"]):
            try:
                phone_types = user.util.get_phone_types()
                serializer = PhoneTypeSerializer(phone_types, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message(
                    "An error occurred while getting the phone types.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )

    def post(self, request, format=None):
        serializer = PhoneTypeSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message(
                "Invalid data",
                True,
                app_url + self.endpoint,
                request.user.id,
                error_message=serializer.errors,
            )

        if has_access(request.user.id, auth_obj):
            try:
                data = serializer.validated_data
                if data.get("id", None) is not None:
                    pt = user.models.PhoneType.objects.get(id=data["id"])
                    pt.phone_type = data["phone_type"]
                    pt.carrier = data["carrier"]
                    pt.save()
                else:
                    user.models.PhoneType(
                        phone_type=data["phone_type"], carrier=data["carrier"]
                    ).save()

                return ret_message("Successfully saved the phone type.")
            except Exception as e:
                return ret_message(
                    "An error occurred while saving the phone type.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    e,
                )
        else:
            return ret_message(
                "You do not have access.",
                True,
                app_url + self.endpoint,
                request.user.id,
            )

    def delete(self, request, format=None):
        try:
            if has_access(request.user.id, "admin"):
                user.util.delete_phone_type(request.query_params["phone_type_id"])
                return ret_message("Successfully deleted the phone type.")
            else:
                return ret_message(
                    "You do not have access.",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )
        except Exception as e:
            return ret_message(
                "An error occurred deleting the phone type.",
                True,
                app_url + self.endpoint,
                request.user.id,
                e,
            )

