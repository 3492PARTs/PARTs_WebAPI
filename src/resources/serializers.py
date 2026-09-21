from rest_framework import serializers

from user.serializers import UserSerializer


class ResourceTypeSerializer(serializers.Serializer):
    """Serializer for resource type objects."""

    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField()
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    void_ind = serializers.CharField(required=False)


class ResourceSerializer(serializers.Serializer):
    """Serializer for resource objects."""

    id = serializers.IntegerField(required=False, allow_null=True)
    resource_type = ResourceTypeSerializer()
    name = serializers.CharField()
    description = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    checked_out = serializers.BooleanField(read_only=True, required=False)
    void_ind = serializers.CharField(required=False)


class ResourceCheckOutSerializer(serializers.Serializer):
    """Serializer for resource check-out/check-in records."""

    id = serializers.IntegerField(required=False, allow_null=True)
    resource = ResourceSerializer(required=False)
    user = UserSerializer(required=False)
    time_out = serializers.DateTimeField(required=False)
    time_in = serializers.DateTimeField(required=False, allow_null=True)
    void_ind = serializers.CharField(required=False)


class CheckOutResourceSerializer(serializers.Serializer):
    """Serializer for the request body used to check out a resource."""

    resource_id = serializers.IntegerField()
    user_id = serializers.IntegerField(required=False)


class CheckInResourceSerializer(serializers.Serializer):
    """Serializer for the request body used to check in a resource."""

    checkout_id = serializers.IntegerField(required=False)
    resource_id = serializers.IntegerField(required=False)
