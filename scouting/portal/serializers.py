from django.db.models import Q
from rest_framework import serializers

from scouting.models import Schedule, Event


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField()
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)


class ScheduleSerializer(serializers.Serializer):
    sch_id = serializers.IntegerField()
    sch_typ = serializers.CharField()
    sch_nm = serializers.CharField()
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.BooleanField()
    user = UserSerializer(required=False, allow_null=True, read_only=True)
    user_name = serializers.CharField(read_only=True)


class ScoutFieldScheduleSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField()
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notification1 = serializers.BooleanField(read_only=True)
    notification2 = serializers.BooleanField(read_only=True)
    notification3 = serializers.BooleanField(read_only=True)

    red_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_three_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_three_id = UserSerializer(
        required=False, allow_null=True, read_only=True)
    scouts = serializers.CharField(read_only=True)


class ScheduleTypeSerializer(serializers.Serializer):
    sch_typ = serializers.CharField()
    sch_nm = serializers.CharField()


class ScheduleByTypeSerializer(serializers.Serializer):
    sch_typ = ScheduleTypeSerializer()
    sch = ScheduleSerializer(many=True, required=False)


class InitSerializer(serializers.Serializer):
    fieldSchedule = ScoutFieldScheduleSerializer(many=True, required=False)
    schedule = ScheduleSerializer(many=True, required=False)
    allFieldSchedule = ScoutFieldScheduleSerializer(many=True, required=False)
    allSchedule = ScheduleByTypeSerializer(many=True, required=False)
    users = UserSerializer(many=True, required=False)
    scheduleTypes = ScheduleTypeSerializer(many=True, required=False)


