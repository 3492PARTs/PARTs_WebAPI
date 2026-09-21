from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

import resources.util
from general.security import ret_message, access_response
from resources.serializers import (
    ResourceTypeSerializer,
    ResourceSerializer,
    ResourceCheckOutSerializer,
    CheckOutResourceSerializer,
    CheckInResourceSerializer,
)

app_url = "resources/"
auth_obj = "resources"


class ResourceTypesView(APIView):
    """
    API endpoint to manage resource types.

    Authentication required: JWT
    Permission required: resources

    GET: Returns all resource types, or a single resource type if resource_type_id is provided
    POST: Creates or updates a resource type
    DELETE: Soft deletes a resource type
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "resource-types/"

    def get(self, request, format=None) -> Response:
        def fun():
            rt_id = request.query_params.get("resource_type_id", None)
            rts = resources.util.get_resource_types(rt_id)
            serializer = ResourceTypeSerializer(rts, many=rt_id is None)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting resource types.",
            fun,
        )

    def post(self, request, format=None) -> Response:
        def fun():
            serializer = ResourceTypeSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            rt = resources.util.save_resource_type(serializer.validated_data)
            return Response(ResourceTypeSerializer(rt).data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while saving resource type.",
            fun,
        )

    def delete(self, request, format=None) -> Response:
        def fun():
            rt_id = request.query_params.get("resource_type_id", None)
            if rt_id is None:
                return ret_message(
                    "resource_type_id is required",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )

            resources.util.delete_resource_type(rt_id)
            return ret_message("Deleted resource type successfully.")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while deleting resource type.",
            fun,
        )


class ResourcesView(APIView):
    """
    API endpoint to manage resources.

    Authentication required: JWT
    Permission required: resources

    GET: Returns all resources, optionally filtered by resource_type_id, or a single resource if resource_id is provided
    POST: Creates or updates a resource
    DELETE: Soft deletes a resource
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "resources/"

    def get(self, request, format=None) -> Response:
        def fun():
            r_id = request.query_params.get("resource_id", None)
            rt_id = request.query_params.get("resource_type_id", None)
            rs = resources.util.get_resources(r_id, rt_id)
            serializer = ResourceSerializer(rs, many=r_id is None)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting resources.",
            fun,
        )

    def post(self, request, format=None) -> Response:
        def fun():
            serializer = ResourceSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            r = resources.util.save_resource(serializer.validated_data)
            return Response(ResourceSerializer(r).data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while saving resource.",
            fun,
        )

    def delete(self, request, format=None) -> Response:
        def fun():
            r_id = request.query_params.get("resource_id", None)
            if r_id is None:
                return ret_message(
                    "resource_id is required",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                )

            resources.util.delete_resource(r_id)
            return ret_message("Deleted resource successfully.")

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while deleting resource.",
            fun,
        )


class ResourceCheckOutsView(APIView):
    """
    API endpoint to view resource checkout history.

    Authentication required: JWT
    Permission required: resources

    GET: Returns checkout records, optionally filtered by resource_id, user_id, and active_only
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "resource-checkouts/"

    def get(self, request, format=None) -> Response:
        def fun():
            checkouts = resources.util.get_checkouts(
                resource_id=request.query_params.get("resource_id", None),
                user_id=request.query_params.get("user_id", None),
                active_only=request.query_params.get("active_only", "false").lower()
                == "true",
            )
            serializer = ResourceCheckOutSerializer(checkouts, many=True)
            return Response(serializer.data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while getting resource checkouts.",
            fun,
        )


class CheckOutResourceView(APIView):
    """
    API endpoint to check out a resource to the requesting user.

    Authentication required: JWT
    Permission required: resources

    POST: Checks out a resource to a user
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "check-out/"

    def post(self, request, format=None) -> Response:
        def fun():
            serializer = CheckOutResourceSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            user_id = serializer.validated_data.get("user_id", None) or request.user.id
            checkout = resources.util.check_out_resource(
                serializer.validated_data["resource_id"], user_id
            )
            return Response(ResourceCheckOutSerializer(checkout).data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while checking out the resource.",
            fun,
        )


class CheckInResourceView(APIView):
    """
    API endpoint to check in a previously checked out resource.

    Authentication required: JWT
    Permission required: resources

    POST: Checks in a resource by checkout_id or resource_id
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = "check-in/"

    def post(self, request, format=None) -> Response:
        def fun():
            serializer = CheckInResourceSerializer(data=request.data)
            if not serializer.is_valid():
                return ret_message(
                    "Invalid data",
                    True,
                    app_url + self.endpoint,
                    request.user.id,
                    error_message=serializer.errors,
                )

            checkout = resources.util.check_in_resource(
                serializer.validated_data.get("checkout_id", None),
                serializer.validated_data.get("resource_id", None),
            )
            return Response(ResourceCheckOutSerializer(checkout).data)

        return access_response(
            app_url + self.endpoint,
            request.user.id,
            auth_obj,
            "An error occurred while checking in the resource.",
            fun,
        )
