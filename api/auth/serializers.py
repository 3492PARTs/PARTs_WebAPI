from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from .models import *


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
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile', 'groups')
        extra_kwargs = {
            'username': {
                'validators': [],
            },
            'groups': {
                'validators': [],
            }
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
