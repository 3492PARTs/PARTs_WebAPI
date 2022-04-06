from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from .models import *

from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.core.validators import EmailValidator, ValidationError


class PermissionSerializer(serializers.ModelSerializer):
    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks"""
        return []

    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, required=False)

    class Meta:
        model = Group
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': []},
        }


class PhoneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneType
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, required=False)
    phone_type = PhoneTypeSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'profile', 'groups', 'is_active', 'phone', 'phone_type')
        extra_kwargs = {
            'username': {
                'validators': [],
            },
            'groups': {
                'validators': [],
            }
        }


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


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name',
                  'last_login', 'date_joined', "is_superuser", "is_active", 'phone', 'phone_type']
        read_only_fields = ['username', 'last_login', 'date_joined']
        extra_kwargs = {
            'email': {'validators': [EmailValidator, ]},
            'password': {'write_only': True},
        }


class UserLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLinks
        fields = '__all__'


class RetMessageSerializer(serializers.Serializer):
    retMessage = serializers.CharField()
    error = serializers.BooleanField()
