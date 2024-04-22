from rest_framework import serializers


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)
    pit_result = serializers.IntegerField()


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
    blue_three_id = UserSerializer(required=False, allow_null=True, read_only=True)
    scouts = serializers.CharField(read_only=True)


class ScheduleTypeSerializer(serializers.Serializer):
    sch_typ = serializers.CharField()
    sch_nm = serializers.CharField()


class SchedulesSerializer(serializers.Serializer):
    field_schedule = ScoutFieldScheduleSerializer(many=True, required=False)
    schedule = ScheduleSerializer(many=True, required=False)
    schedule_types = ScheduleTypeSerializer(many=True, required=False)
