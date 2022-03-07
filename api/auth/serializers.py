from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from .models import *

from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.core.validators import EmailValidator, ValidationError
from django.contrib.auth import get_user_model


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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'validators': [],
            }
        }


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    groups = GroupSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'profile', 'groups')
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


class ScoutScheduleSerializer(serializers.Serializer):
    scout_sch_id = serializers.IntegerField(required=False)
    user = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.IntegerField()
    sq_typ = serializers.CharField()
    sq_nm = serializers.CharField(required=False)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField(required=False)
    notify = serializers.CharField(required=False)
    void_ind = serializers.CharField()

    st_time_str = serializers.CharField(required=False)
    end_time_str = serializers.CharField(required=False)


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name',
                  'last_login', 'date_joined', "is_staff", "is_superuser", "is_active", "image"]
        read_only_fields = ['username', 'last_login', 'date_joined']
        extra_kwargs = {
            'email': {'validators': [EmailValidator, ]},
            'password': {'write_only': True},
        }


class UserLinksSerializer(serializers.Serializer):
    MenuName = serializers.CharField()
    RouterLink = serializers.CharField()


class PhoneTypeSerializer(serializers.Serializer):
    phone_type_id = serializers.IntegerField(required=False)
    carrier = serializers.CharField()
    phone_type = serializers.CharField()


class RetMessageSerializer(serializers.Serializer):
    retMessage = serializers.CharField()
    error = serializers.BooleanField()


class ErrorLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = ErrorLog
        fields = '__all__'
