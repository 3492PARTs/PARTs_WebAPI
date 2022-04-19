from rest_framework import serializers
from .models import ErrorLog
from user.serializers import UserSerializer, GroupSerializer, PhoneTypeSerializer


class InitSerializer(serializers.Serializer):
    users = UserSerializer(many=True)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)


class SaveUserSerializer(serializers.Serializer):
    user = UserSerializer()
    groups = GroupSerializer(many=True)


class ErrorLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = ErrorLog
        fields = '__all__'
