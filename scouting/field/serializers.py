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


class MatchSerializer(serializers.Serializer):
    match_id = serializers.CharField(read_only=True)
    event_id = serializers.IntegerField(read_only=True)
    match_number = serializers.IntegerField()
    time = serializers.DateTimeField()
    blue_one = serializers.IntegerField()
    blue_two = serializers.IntegerField()
    blue_three = serializers.IntegerField()
    red_one = serializers.IntegerField()
    red_two = serializers.IntegerField()
    red_three = serializers.IntegerField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField()
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)


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

    red_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_three_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_three_check_in = serializers.DateTimeField(required=False, allow_null=True)

    scouts = serializers.CharField(read_only=True)


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

    is_condition = serializers.CharField()


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

    is_condition = serializers.CharField()


class SaveScoutFieldSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    team = serializers.CharField()
    match = serializers.CharField(required=False)


class ScoutColSerializer(serializers.Serializer):
    PropertyName = serializers.CharField()
    ColLabel = serializers.CharField()
    order = serializers.CharField()
    scorable = serializers.BooleanField()


class ScoutResultAnswerSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance


class ScoutFieldSerializer(serializers.Serializer):
    scout_field_id = serializers.IntegerField()
    # response = serializers.IntegerField()
    # event = serializers.IntegerField()
    # team_no = serializers.IntegerField()
    # user = serializers.IntegerField()
    # time = serializers.DateTimeField()
    # match = serializers.IntegerField()
    # void_ind = serializers.CharField()


class ScoutFieldResultsSerializer(serializers.Serializer):
    scoutCols = ScoutColSerializer(many=True)
    scoutAnswers = ScoutResultAnswerSerializer(many=True)
    current_season = SeasonSerializer()
    current_event = EventSerializer()
    removed_responses = ScoutFieldSerializer(many=True)
