from rest_framework import serializers


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)


class MatchSerializer(serializers.Serializer):
    match_id = serializers.CharField(read_only=True)
    event_id = serializers.IntegerField(read_only=True)
    match_number = serializers.IntegerField()
    time = serializers.DateTimeField()
    blue_one_id = serializers.IntegerField()
    blue_two_id = serializers.IntegerField()
    blue_three_id = serializers.IntegerField()
    red_one_id = serializers.IntegerField()
    red_two_id = serializers.IntegerField()
    red_three_id = serializers.IntegerField()


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

    red_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_three_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_three_id = UserSerializer(
        required=False, allow_null=True, read_only=True)


class QuestionOptionsSerializer(serializers.Serializer):
    question_opt_id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField(read_only=True)
    option = serializers.CharField()
    active = serializers.CharField()


class QuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)

    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField()
    question_typ = serializers.CharField()
    question_typ_nm = serializers.CharField(required=False, allow_blank=True)
    form_sub_typ = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_sub_nm = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_typ = serializers.CharField()

    questionoptions_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True)

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ScoutFieldSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    #team = serializers.CharField(required=False)
    scoutFieldSchedule = ScoutFieldScheduleSerializer()
    matches = MatchSerializer(many=True, required=False)


class SaveScoutFieldSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    team = serializers.CharField()
    match = serializers.CharField(required=False)


class ScoutColSerializer(serializers.Serializer):
    PropertyName = serializers.CharField()
    ColLabel = serializers.CharField()
    order = serializers.CharField()


class ScoutResultAnswerSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance


class ScoutFieldResultsSerializer(serializers.Serializer):
    scoutCols = ScoutColSerializer(many=True)
    scoutAnswers = ScoutResultAnswerSerializer(many=True)
