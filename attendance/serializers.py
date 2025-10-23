from rest_framework import serializers

from scouting.serializers import UserSerializer


class AttendanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer()
    time = serializers.DateTimeField()
