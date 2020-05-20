from rest_framework import serializers
from api.api.models import *
from api.auth.serializers import UserSerializer, GroupSerializer, PhoneTypeSerializer


class InitSerializer(serializers.Serializer):
    users = UserSerializer(many=True)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)


class SaveUserSerializer(serializers.Serializer):
    user = UserSerializer(read_only=False)
    groups = GroupSerializer(many=True)
