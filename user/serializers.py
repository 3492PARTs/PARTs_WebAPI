from rest_framework import serializers

from django.contrib.auth.password_validation import (
    validate_password,
    get_default_password_validators,
)
from django.core.validators import ValidationError


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
    phone_type_id = serializers.IntegerField(read_only=True)
    carrier = serializers.CharField()
    phone_type = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    username = serializers.CharField()
    email = serializers.CharField()
    name = serializers.CharField(required=False)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField(allow_blank=True)
    discord_user_id = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    groups = GroupSerializer(many=True, required=False)
    phone_type = PhoneTypeSerializer(required=False, allow_null=True)
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)

    image = serializers.CharField(required=False)


class UserCreationSerializer(serializers.Serializer):
    """
    User serializer, used only for validation of fields upon user registration.
    """

    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        ]

    def validate_password1(self, validated_data):
        try:
            validate_password(
                validated_data, password_validators=get_default_password_validators()
            )

        except ValidationError as e:
            raise serializers.ValidationError({"password": str(e)})
        return validated_data


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)


class LinkSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True, required=False)
    permission = PermissionSerializer(allow_null=True, required=False)
    menu_name = serializers.CharField()
    routerlink = serializers.CharField()
    order = serializers.IntegerField()


class RetMessageSerializer(serializers.Serializer):
    retMessage = serializers.CharField()
    error = serializers.BooleanField()
    errorMessage = serializers.CharField(required=False)


class GetAlertsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    channel_send_id = serializers.IntegerField()
    subject = serializers.CharField()
    body = serializers.CharField()
    staged_time = serializers.DateTimeField()
