from rest_framework import serializers


class SeasonSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(read_only=True)
    season = serializers.CharField()
    current = serializers.CharField()


class EventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=False)
    season_id = serializers.IntegerField()
    event_nm = serializers.CharField()
    date_st = serializers.DateTimeField()
    date_end = serializers.DateTimeField()
    event_cd = serializers.CharField()
    event_url = serializers.CharField(required=False)
    address = serializers.CharField()
    city = serializers.CharField()
    state_prov = serializers.CharField()
    postal_code = serializers.CharField()
    location_name = serializers.CharField()
    gmaps_url = serializers.CharField(required=False)
    webcast_url = serializers.CharField(required=False)
    timezone = serializers.CharField()
    current = serializers.CharField()
    competition_page_active = serializers.CharField()
    void_ind = serializers.CharField(default="n")


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)


class QuestionOptionsSerializer(serializers.Serializer):
    question_opt_id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField(read_only=True)
    option = serializers.CharField()
    active = serializers.CharField()


class QuestionTypeSerializer(serializers.Serializer):
    question_typ = serializers.CharField()
    question_typ_nm = serializers.CharField()
    is_list = serializers.CharField()


class ScoutQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField()
    season_id = serializers.IntegerField(read_only=True)
    scorable = serializers.BooleanField()


class QuestionConditionQuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)

    question = serializers.CharField()
    table_col_width = serializers.CharField()
    order = serializers.IntegerField()
    required = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    active = serializers.CharField()
    question_typ = QuestionTypeSerializer()
    form_sub_typ = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    form_sub_nm = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    form_typ = serializers.CharField()
    display_value = serializers.CharField(read_only=True)

    questionoption_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True
    )

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    scout_question = ScoutQuestionSerializer(required=False, allow_null=True)

    is_condition = serializers.CharField(required=False)


class QuestionConditionSerializer(serializers.Serializer):
    question_condition_id = serializers.IntegerField(required=False)
    condition = serializers.CharField()
    question_from = QuestionConditionQuestionSerializer()
    question_to = QuestionConditionQuestionSerializer()
    active = serializers.CharField()


class QuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)

    question = serializers.CharField()
    table_col_width = serializers.CharField()
    order = serializers.IntegerField()
    required = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    active = serializers.CharField()
    question_typ = QuestionTypeSerializer()
    form_sub_typ = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    form_sub_nm = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    form_typ = serializers.CharField()
    display_value = serializers.CharField(read_only=True)

    questionoption_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True
    )

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    scout_question = ScoutQuestionSerializer(required=False, allow_null=True)

    conditions = QuestionConditionSerializer(required=False, many=True)

    is_condition = serializers.CharField(required=False)


class InitSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    comp_teams = TeamSerializer(many=True, required=False)


class ScoutAnswerSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)


class ScoutPitResponseAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_null=True)


class ScoutPitImageSerializer(serializers.Serializer):
    scout_pit_img_id = serializers.IntegerField(required=False)
    pic = serializers.CharField()
    default = serializers.BooleanField()


class ScoutPitResponseSerializer(serializers.Serializer):
    scout_pit_id = serializers.IntegerField()
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()
    pics = ScoutPitImageSerializer(many=True, required=False)
    responses = ScoutPitResponseAnswerSerializer(many=True)


class ScoutPitResponsesSerializer(serializers.Serializer):
    teams = ScoutPitResponseSerializer(many=True)
    current_season = SeasonSerializer()
    current_event = EventSerializer()


class PitTeamDataSerializer(serializers.Serializer):
    response_id = serializers.IntegerField(required=False)
    questions = QuestionSerializer(required=False, many=True)
    pics = ScoutPitImageSerializer(many=True, required=False)
