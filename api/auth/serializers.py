from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'phone_type')
        extra_kwargs = {
            'username': {
                'validators': [],
            }
        }


class AuthGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthGroup
        fields = '__all__'


class UserLinksSerializer(serializers.Serializer):
    MenuName = serializers.CharField()
    RouterLink = serializers.CharField()


class PhoneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneType
        fields = '__all__'

class RetMessageSerializer(serializers.Serializer):
    retMessage = serializers.CharField()
    error = serializers.BooleanField()
