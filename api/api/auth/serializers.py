from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ('username', 'email', 'first_name', 'last_name')


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=40, min_length=40)
