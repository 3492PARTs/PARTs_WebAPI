from rest_framework import serializers

from form.serializers import QuestionSerializer, FormSubTypeSerializer, QuestionFlowSerializer
from user.serializers import UserSerializer


class SeasonSerializer(serializers.Serializer):
    season_id = serializers.IntegerField()
    season = serializers.CharField()
    current = serializers.CharField()


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)
    pit_result = serializers.IntegerField(required=False)
    rank = serializers.IntegerField(required=False)


class EventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField()
    teams = TeamSerializer(many=True, required=False)
    event_nm = serializers.CharField()
    date_st = serializers.DateTimeField()
    date_end = serializers.DateTimeField()
    event_cd = serializers.CharField()
    event_url = serializers.CharField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField()
    state_prov = serializers.CharField()
    postal_code = serializers.CharField(required=False, allow_null=True)
    location_name = serializers.CharField(required=False, allow_null=True)
    gmaps_url = serializers.CharField(required=False, allow_null=True)
    webcast_url = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    timezone = serializers.CharField(required=False, allow_null=True)
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

    blue_one_id = serializers.IntegerField()
    blue_one_rank = serializers.IntegerField(allow_null=True)
    blue_one_field_response = serializers.BooleanField()

    blue_two_id = serializers.IntegerField()
    blue_two_rank = serializers.IntegerField(allow_null=True)
    blue_two_field_response = serializers.BooleanField()

    blue_three_id = serializers.IntegerField()
    blue_three_rank = serializers.IntegerField(allow_null=True)
    blue_three_field_response = serializers.BooleanField()

    red_one_id = serializers.IntegerField()
    red_one_rank = serializers.IntegerField(allow_null=True)
    red_one_field_response = serializers.BooleanField()

    red_two_id = serializers.IntegerField()
    red_two_rank = serializers.IntegerField(allow_null=True)
    red_two_field_response = serializers.BooleanField()

    red_three_id = serializers.IntegerField()
    red_three_rank = serializers.IntegerField(allow_null=True)
    red_three_field_response = serializers.BooleanField()

    comp_level = CompetitionLevelSerializer()


class ScheduleSerializer(serializers.Serializer):
    sch_id = serializers.IntegerField()
    sch_typ = serializers.CharField()
    sch_nm = serializers.CharField()
    event_id = serializers.IntegerField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.BooleanField()
    user = UserSerializer(required=False, allow_null=True)
    user_name = serializers.CharField(required=False, allow_null=True)


class ScoutFieldScheduleSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField()
    event_id = serializers.IntegerField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notification1 = serializers.BooleanField()
    notification2 = serializers.BooleanField()
    notification3 = serializers.BooleanField()

    red_one_id = UserSerializer(required=False, allow_null=True)
    red_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_two_id = UserSerializer(required=False, allow_null=True)
    red_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_three_id = UserSerializer(required=False, allow_null=True)
    red_three_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_one_id = UserSerializer(required=False, allow_null=True)
    blue_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_two_id = UserSerializer(required=False, allow_null=True)
    blue_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_three_id = UserSerializer(required=False, allow_null=True)
    blue_three_check_in = serializers.DateTimeField(required=False, allow_null=True)
    scouts = serializers.CharField()


class ScheduleTypeSerializer(serializers.Serializer):
    sch_typ = serializers.CharField()
    sch_nm = serializers.CharField()


class MatchStrategySerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True, required=False)
    match = MatchSerializer()
    user = UserSerializer()
    strategy = serializers.CharField()
    img_url = serializers.CharField(required=False, allow_null=True)
    time = serializers.DateTimeField(read_only=True)
    display_value = serializers.CharField()


class SaveMatchStrategySerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True, required=False)
    match_id = serializers.CharField()
    user_id = serializers.IntegerField()
    strategy = serializers.CharField()
    img = serializers.FileField(allow_null=True, required=False)


class TeamNoteSerializer(serializers.Serializer):
    team_note_id = serializers.IntegerField(read_only=True)
    team_id = serializers.IntegerField()
    match_id = serializers.IntegerField(required=False)
    user = UserSerializer()
    note = serializers.CharField()
    time = serializers.DateTimeField(read_only=True)


class FieldFormSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(required=False, allow_null=True)
    img = serializers.FileField(required=False, allow_null=True)
    img_url = serializers.CharField(required=False, allow_null=True)
    inv_img = serializers.FileField(required=False, allow_null=True)
    inv_img_url = serializers.CharField(required=False, allow_null=True)
    full_img = serializers.FileField(required=False, allow_null=True)
    full_img_url = serializers.CharField(required=False, allow_null=True)


class FormSubTypeFormSerializer(serializers.Serializer):
    form_sub_typ = FormSubTypeSerializer()
    questions = QuestionSerializer(many=True)
    # conditional_questions = QuestionSerializer(many=True)
    question_flows = QuestionFlowSerializer(many=True)


class FieldFormFormSerializer(serializers.Serializer):
    field_form = FieldFormSerializer()
    form_sub_types = FormSubTypeFormSerializer(many=True, required=False)


class AllianceSelectionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    event = EventSerializer()
    team = TeamSerializer()
    note = serializers.CharField(allow_blank=True)
    order = serializers.IntegerField()


class AllScoutInfoSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventSerializer(many=True)
    teams = TeamSerializer(many=True)
    matches = MatchSerializer(many=True)
    schedules = ScheduleSerializer(many=True)
    scout_field_schedules = ScoutFieldScheduleSerializer(many=True)
    schedule_types = ScheduleTypeSerializer(many=True)
    team_notes = TeamNoteSerializer(many=True)
    match_strategies = MatchStrategySerializer(many=True)
    field_form_form = FieldFormFormSerializer()
    alliance_selections = AllianceSelectionSerializer(many=True)