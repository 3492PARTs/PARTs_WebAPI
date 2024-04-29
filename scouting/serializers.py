from rest_framework import serializers


class SeasonSerializer(serializers.Serializer):
    season_id = serializers.IntegerField()
    season = serializers.CharField()
    current = serializers.CharField()


class EventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    season_id = serializers.IntegerField()
    event_nm = serializers.CharField()
    date_st = serializers.DateTimeField()
    date_end = serializers.DateTimeField()
    event_cd = serializers.CharField()
    event_url = serializers.CharField(required=False, allow_null=True)
    address = serializers.CharField()
    city = serializers.CharField()
    state_prov = serializers.CharField()
    postal_code = serializers.CharField()
    location_name = serializers.CharField()
    gmaps_url = serializers.CharField(required=False, allow_null=True)
    webcast_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    timezone = serializers.CharField()
    current = serializers.CharField()
    competition_page_active = serializers.CharField()
    void_ind = serializers.CharField(default="n")


class CompetitionLevelSerializer(serializers.Serializer):
    comp_lvl_typ = serializers.CharField()
    comp_lvl_typ_nm = serializers.CharField()
    comp_lvl_order = serializers.IntegerField()


class MatchSerializer(serializers.Serializer):
    match_id = serializers.CharField()
    event_id = serializers.IntegerField()
    match_number = serializers.IntegerField()
    red_score = serializers.IntegerField()
    blue_score = serializers.IntegerField()
    time = serializers.DateTimeField(allow_null=True)

    blue_one = serializers.IntegerField()
    blue_one_rank = serializers.IntegerField(allow_null=True)
    blue_one_field_response = serializers.BooleanField()

    blue_two = serializers.IntegerField()
    blue_two_rank = serializers.IntegerField(allow_null=True)
    blue_two_field_response = serializers.BooleanField()

    blue_three = serializers.IntegerField()
    blue_three_rank = serializers.IntegerField(allow_null=True)
    blue_three_field_response = serializers.BooleanField()

    red_one = serializers.IntegerField()
    red_one_rank = serializers.IntegerField(allow_null=True)
    red_one_field_response = serializers.BooleanField()

    red_two = serializers.IntegerField()
    red_two_rank = serializers.IntegerField(allow_null=True)
    red_two_field_response = serializers.BooleanField()

    red_three = serializers.IntegerField()
    red_three_rank = serializers.IntegerField(allow_null=True)
    red_three_field_response = serializers.BooleanField()

    comp_level = CompetitionLevelSerializer()


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)
    pit_result = serializers.IntegerField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField(allow_blank=True)
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)


class ScheduleSerializer(serializers.Serializer):
    sch_id = serializers.IntegerField()
    sch_typ = serializers.CharField()
    sch_nm = serializers.CharField()
    event_id = serializers.IntegerField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.BooleanField()
    user = UserSerializer(required=False, allow_null=True)
    user_name = serializers.CharField(read_only=True)


class ScoutFieldScheduleSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField()
    event_id = serializers.IntegerField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notification1 = serializers.BooleanField()
    notification2 = serializers.BooleanField()
    notification3 = serializers.BooleanField()

    red_one_id = UserSerializer(required=False, allow_null=True)
    red_two_id = UserSerializer(required=False, allow_null=True)
    red_three_id = UserSerializer(required=False, allow_null=True)
    blue_one_id = UserSerializer(required=False, allow_null=True)
    blue_two_id = UserSerializer(required=False, allow_null=True)
    blue_three_id = UserSerializer(required=False, allow_null=True)
    scouts = serializers.CharField()


class ScheduleTypeSerializer(serializers.Serializer):
    sch_typ = serializers.CharField()
    sch_nm = serializers.CharField()


class AllScoutInfoSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventSerializer(many=True)
    teams = TeamSerializer(many=True)
    matches = MatchSerializer(many=True)
    schedules = ScheduleSerializer(many=True)
    scout_field_schedules = ScoutFieldScheduleSerializer(many=True)
    schedule_types = ScheduleTypeSerializer(many=True)
