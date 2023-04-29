from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.core.validators import ValidationError


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    content_type_id = serializers.IntegerField(read_only=True)
    codename = serializers.CharField()


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    permissions = PermissionSerializer(many=True, required=False)


class PhoneTypeSerializer(serializers.Serializer):
    phone_type_id = serializers.IntegerField(read_only=True)
    carrier = serializers.CharField()
    phone_type = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField()

    groups = GroupSerializer(many=True, required=False)
    phone_type = PhoneTypeSerializer(required=False, allow_null=True)
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)


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
        fields = ['username', 'email', 'password1',
                  'password2', 'first_name', 'last_name']

    def validate_password1(self, validated_data):
        try:
            validate_password(
                validated_data, password_validators=get_default_password_validators())

        except ValidationError as e:
            raise serializers.ValidationError({'password': str(e)})
        return validated_data


"""
class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name',
                  'last_login', 'date_joined', "is_superuser", "is_active", 'phone', 'phone_type']
        read_only_fields = ['username', 'last_login', 'date_joined']
        extra_kwargs = {
            'email': {'validators': [EmailValidator, ]},
            'password': {'write_only': True},
        }
"""


class UserLinksSerializer(serializers.Serializer):
    user_links_id = serializers.IntegerField(read_only=True)
    permission = PermissionSerializer()
    menu_name = serializers.CharField()
    routerlink = serializers.CharField()
    order = serializers.IntegerField()


class RetMessageSerializer(serializers.Serializer):
    retMessage = serializers.CharField()
    error = serializers.BooleanField()


class SaveUserPushNotificationSubscriptionObjectSerializer(serializers.Serializer):
    endpoint = serializers.CharField()
    p256dh = serializers.CharField()
    auth = serializers.CharField()
