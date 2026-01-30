from rest_framework import serializers

from scouting.serializers import UserSerializer


class MeetingTypeSerializer(serializers.Serializer):
    meeting_typ = serializers.CharField()
    meeting_nm = serializers.CharField()


class MeetingSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    meeting_typ = MeetingTypeSerializer()
    title = serializers.CharField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    ended = serializers.BooleanField()
    void_ind = serializers.CharField()


class AttendanceApprovalTypeSerializer(serializers.Serializer):
    approval_typ = serializers.CharField()
    approval_nm = serializers.CharField()


class AttendanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    user = UserSerializer()
    meeting = MeetingSerializer(allow_null=True, required=False)
    time_in = serializers.DateTimeField()
    time_out = serializers.DateTimeField(allow_null=True, required=False)
    absent = serializers.BooleanField()
    approval_typ = AttendanceApprovalTypeSerializer()
    void_ind = serializers.CharField()


class AttendanceReportSerializer(serializers.Serializer):
    user = UserSerializer()
    reg_time = serializers.FloatField()
    reg_time_percentage = serializers.FloatField()
    event_time = serializers.FloatField()
    event_time_percentage = serializers.FloatField()


class MeetingHoursSerializer(serializers.Serializer):
    hours = serializers.FloatField()
    hours_future = serializers.FloatField()
    bonus_hours = serializers.FloatField()
    event_hours = serializers.FloatField()
