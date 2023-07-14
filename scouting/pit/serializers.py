from rest_framework import serializers


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


class QuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)

    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField()
    question_typ = QuestionTypeSerializer()
    form_sub_typ = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_sub_nm = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_typ = serializers.CharField()

    questionoptions_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True)

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class InitSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    comp_teams = TeamSerializer(many=True, required=False)


class ScoutAnswerSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)


class ScoutPitResultAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_null=True)


class ScoutPitResultsSerializer(serializers.Serializer):
    teamNo = serializers.CharField()
    teamNm = serializers.CharField()
    pic = serializers.CharField()
    results = ScoutPitResultAnswerSerializer(many=True)


class PitTeamDataSerializer(serializers.Serializer):
    questions = QuestionSerializer(required=False, many=True)
    pic = serializers.CharField()
