from rest_framework import serializers

class QuestionTypeSerializer(serializers.Serializer):
    question_typ = serializers.CharField()
    question_typ_nm = serializers.CharField()
    is_list = serializers.CharField()


class FormTypeSerializer(serializers.Serializer):
    form_typ = serializers.CharField(read_only=True)
    form_nm = serializers.CharField()


class FormSubTypeSerializer(serializers.Serializer):
    form_sub_typ = serializers.CharField()
    form_sub_nm = serializers.CharField()
    form_typ_id = serializers.CharField()


class QuestionOptionsSerializer(serializers.Serializer):
    question_opt_id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField(read_only=True)
    option = serializers.CharField()
    active = serializers.CharField()


class ScoutQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField()
    season_id = serializers.IntegerField(read_only=True)
    scorable = serializers.BooleanField()


class QuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)

    question = serializers.CharField()
    order = serializers.IntegerField()
    required = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    active = serializers.CharField()
    question_typ = QuestionTypeSerializer()
    form_sub_typ = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_sub_nm = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_typ = serializers.CharField()
    display_value = serializers.CharField(read_only=True)

    questionoption_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True)

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    scout_question = ScoutQuestionSerializer(required=False, allow_null=True)


class SaveScoutSerializer(serializers.Serializer):
    question_answers = QuestionSerializer(many=True)
    team = serializers.CharField()
    match = serializers.CharField(required=False)
    form_typ = serializers.CharField()


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)


class SaveResponseSerializer(serializers.Serializer):
    question_answers = QuestionSerializer(many=True)
    form_typ = serializers.CharField()


class QuestionInitializationSerializer(serializers.Serializer):
    questions = QuestionSerializer(many=True)
    question_types = QuestionTypeSerializer(many=True)
    form_sub_types = FormSubTypeSerializer(many=True, required=False)


class ResponseSerializer(serializers.Serializer):
    response_id = serializers.IntegerField()
    form_typ = serializers.CharField()
    time = serializers.DateTimeField()
    questionanswer_set = QuestionSerializer(many=True)