from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField()
    content_type_id = serializers.IntegerField(read_only=True)
    codename = serializers.CharField()


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField()
    permissions = PermissionSerializer(many=True, required=False)


class PhoneTypeSerializer(serializers.Serializer):
    phone_type_id = serializers.IntegerField(required=False)
    carrier = serializers.CharField()
    phone_type = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField(required=False, allow_null=True)
    discord_user_id = serializers.CharField(required=False, allow_null=True)

    groups = GroupSerializer(many=True, required=False)
    phone_type = PhoneTypeSerializer(required=False, allow_null=True)
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)


class InitSerializer(serializers.Serializer):
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)


class ErrorLogSerializer(serializers.Serializer):
    error_log_id = serializers.IntegerField(read_only=True)
    path = serializers.CharField()
    message = serializers.CharField()
    exception = serializers.CharField()
    traceback = serializers.CharField()
    time = serializers.DateTimeField()

    user = UserSerializer(required=False)

