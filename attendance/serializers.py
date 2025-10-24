from rest_framework import serializers

from scouting.serializers import UserSerializer


class MeetingSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()


class AttendanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    user = UserSerializer()
    time_in = serializers.DateTimeField()
    time_out = serializers.DateTimeField()
    bonus_approved = serializers.BooleanField()
