from rest_framework import serializers

from scouting.serializers import UserSerializer


class MeetingSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    bonus = serializers.BooleanField()
    void_ind = serializers.CharField()


class AttendanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    user = UserSerializer()
    meeting = MeetingSerializer(allow_null=True, required=False)
    time_in = serializers.DateTimeField()
    time_out = serializers.DateTimeField(allow_null=True, required=False)
    absent = serializers.BooleanField()
    approved = serializers.BooleanField()
    void_ind = serializers.CharField()


class AttendanceReportSerializer(serializers.Serializer):
    user = UserSerializer()
    time = serializers.FloatField()
    percentage = serializers.FloatField()
