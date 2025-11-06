from rest_framework import serializers

from scouting.serializers import UserSerializer
from user.serializers import GroupSerializer, PhoneTypeSerializer


class InitSerializer(serializers.Serializer):
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)


class ErrorLogSerializer(serializers.Serializer):
    error_log_id = serializers.IntegerField(read_only=True)
    path = serializers.CharField()
    message = serializers.CharField()
    exception = serializers.CharField()
    error_message = serializers.CharField()
    traceback = serializers.CharField()
    time = serializers.DateTimeField()

    user = UserSerializer(required=False)
