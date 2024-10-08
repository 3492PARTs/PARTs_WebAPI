from rest_framework import serializers


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()


class EventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(read_only=True)
    season_id = serializers.IntegerField(read_only=True)
    event_nm = serializers.CharField()
    date_st = serializers.DateTimeField()
    date_end = serializers.DateTimeField()
    event_cd = serializers.CharField()
    event_url = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state_prov = serializers.CharField()
    postal_code = serializers.CharField()
    location_name = serializers.CharField()
    gmaps_url = serializers.CharField()
    webcast_url = serializers.CharField()
    timezone = serializers.CharField()
    current = serializers.CharField()
    competition_page_active = serializers.CharField()


class CompetitionLevelSerializer(serializers.Serializer):
    comp_lvl_typ = serializers.CharField()
    comp_lvl_typ_nm = serializers.CharField()
    comp_lvl_order = serializers.IntegerField()


class MatchSerializer(serializers.Serializer):
    match_id = serializers.CharField(read_only=True)
    event_id = serializers.IntegerField(read_only=True)
    match_number = serializers.IntegerField()
    red_score = serializers.IntegerField()
    blue_score = serializers.IntegerField()
    time = serializers.DateTimeField()
    blue_one_id = serializers.IntegerField()
    blue_one_rank = serializers.IntegerField(allow_null=True)
    blue_two_id = serializers.IntegerField()
    blue_two_rank = serializers.IntegerField(allow_null=True)
    blue_three_id = serializers.IntegerField()
    blue_three_rank = serializers.IntegerField(allow_null=True)
    red_one_id = serializers.IntegerField()
    red_one_rank = serializers.IntegerField(allow_null=True)
    red_two_id = serializers.IntegerField()
    red_two_rank = serializers.IntegerField(allow_null=True)
    red_three_id = serializers.IntegerField()
    red_three_rank = serializers.IntegerField(allow_null=True)

    comp_level = CompetitionLevelSerializer(read_only=True)


class InitSerializer(serializers.Serializer):
    event = EventSerializer()
    matches = MatchSerializer(many=True, required=False)
    teams = TeamSerializer(many=True, required=False)


class ScoutPitResultAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_null=True)


class ScoutPitImageSerializer(serializers.Serializer):
    scout_pit_img_id = serializers.IntegerField(required=False)
    pic = serializers.CharField()
    default = serializers.BooleanField()


class ScoutPitResultsSerializer(serializers.Serializer):
    teamNo = serializers.CharField()
    teamNm = serializers.CharField()
    pics = ScoutPitImageSerializer(many=True, required=False)
    results = ScoutPitResultAnswerSerializer(many=True)


class ScoutColSerializer(serializers.Serializer):
    PropertyName = serializers.CharField()
    ColLabel = serializers.CharField()
    scorable = serializers.BooleanField()
    order = serializers.CharField()


class ScoutResultAnswerSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance


class TeamNoteSerializer(serializers.Serializer):
    team_note_id = serializers.IntegerField(read_only=True)
    team_no = serializers.IntegerField()
    match_id = serializers.CharField(read_only=True)
    note = serializers.CharField()
    time = serializers.DateTimeField()


class MatchPlanningSerializer(serializers.Serializer):
    team = TeamSerializer()
    pitData = ScoutPitResultsSerializer()
    fieldCols = ScoutColSerializer(many=True)
    fieldAnswers = ScoutResultAnswerSerializer(many=True)
    notes = TeamNoteSerializer(many=True)
    alliance = serializers.CharField()


class SaveTeamNoteSerializer(serializers.Serializer):
    team_note_id = serializers.IntegerField(read_only=True)
    team_no = serializers.IntegerField()
    match_id = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    note = serializers.CharField()
