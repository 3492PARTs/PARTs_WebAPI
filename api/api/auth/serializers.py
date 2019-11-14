from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ('username', 'email', 'first_name', 'last_name')


class UserLinksSerializer(serializers.Serializer):
    MenuName = serializers.CharField()
    RouterLink = serializers.CharField()


class RetMessageSerializer(serializers.Serializer):
    retMessage = serializers.CharField()
    error = serializers.BooleanField()
