from rest_framework import serializers

from general.cloudinary import allowed_file


class ScoutQuestionTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    scorable = serializers.CharField(required=False, allow_null=True)


class QuestionTypeSerializer(serializers.Serializer):
    question_typ = serializers.CharField()
    question_typ_nm = serializers.CharField()
    is_list = serializers.CharField()
    scout_question_type = ScoutQuestionTypeSerializer(required=False, allow_null=True)


class FormTypeSerializer(serializers.Serializer):
    form_typ = serializers.CharField()
    form_nm = serializers.CharField(required=False, allow_blank=True)


class FormSubTypeSerializer(serializers.Serializer):
    form_sub_typ = serializers.CharField()
    form_sub_nm = serializers.CharField()
    form_typ_id = serializers.CharField()
    order = serializers.IntegerField()


class QuestionOptionsSerializer(serializers.Serializer):
    question_opt_id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField(read_only=True)
    option = serializers.CharField()
    active = serializers.CharField()


class ScoutQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)


class QuestionConditionTypeSerializer(serializers.Serializer):
    question_condition_typ = serializers.CharField()
    question_condition_nm = serializers.CharField()


class QuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)
    flow_id_set = serializers.ListField()

    question = serializers.CharField()
    svg = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    table_col_width = serializers.CharField()
    order = serializers.IntegerField()
    required = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    svg = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    x = serializers.FloatField(required=False, allow_null=True)
    y = serializers.FloatField(required=False, allow_null=True)
    width = serializers.FloatField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    icon = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    icon_only = serializers.BooleanField(required=False, allow_null=True)
    value_multiplier = serializers.IntegerField(required=False, allow_null=True)
    active = serializers.CharField()
    question_typ = QuestionTypeSerializer()
    form_typ = FormTypeSerializer()
    form_sub_typ = FormSubTypeSerializer(required=False, allow_null=True)
    display_value = serializers.CharField(read_only=True)

    questionoption_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True
    )

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    scout_question = ScoutQuestionSerializer(required=False, allow_null=True)

    question_conditional_on = serializers.IntegerField(allow_null=True)
    question_condition_value = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    question_condition_typ = QuestionConditionTypeSerializer(
        required=False, allow_null=True
    )
    conditional_question_id_set = serializers.ListField()


class ResponseSerializer(serializers.Serializer):
    response_id = serializers.IntegerField()
    form_typ = serializers.CharField()
    time = serializers.DateTimeField()
    questionanswer_set = QuestionSerializer(many=True)
    archive_ind = serializers.CharField()


class QuestionAggregateTypeSerializer(serializers.Serializer):
    question_aggregate_typ = serializers.CharField()
    question_aggregate_nm = serializers.CharField()


class QuestionAggregateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    field_name = serializers.CharField()
    question_aggregate_typ = QuestionAggregateTypeSerializer(required=False)
    questions = QuestionSerializer(many=True)
    active = serializers.CharField()


class QuestionConditionSerializer(serializers.Serializer):
    question_condition_id = serializers.IntegerField(required=False)
    question_condition_typ = QuestionConditionTypeSerializer()
    value = serializers.CharField(allow_blank=True)
    question_from = QuestionSerializer()
    question_to = QuestionSerializer()
    active = serializers.CharField()

class FlowQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    flow_id = serializers.IntegerField(required=False, allow_null=True)
    question = QuestionSerializer()
    order = serializers.IntegerField()
    active = serializers.CharField()


class FlowSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField()
    single_run = serializers.BooleanField()
    form_typ = FormTypeSerializer()
    form_sub_typ = FormSubTypeSerializer(required=False, allow_null=True)
    flow_questions = FlowQuestionSerializer(many=True, required=False)
    void_ind = serializers.CharField()

    flow_conditional_on = serializers.IntegerField(allow_null=True)
    has_conditions = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class FlowConditionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    flow_from = FlowSerializer()
    flow_to = FlowSerializer()
    active = serializers.CharField()


class FlowAnswerSerializer(serializers.Serializer):
    question = QuestionSerializer()
    value = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    value_time = serializers.TimeField()


class AnswerSerializer(serializers.Serializer):
    question = QuestionSerializer(required=False, allow_null=True)
    flow = FlowSerializer(required=False, allow_null=True)
    value = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    flow_answers = FlowAnswerSerializer(
        many=True, required=False, allow_null=True
    )


class ScoutFieldFormResponseSerializer(serializers.Serializer):
    answers = AnswerSerializer(many=True)
    team_id = serializers.CharField()
    match_id = serializers.CharField(required=False, allow_null=True)
    form_typ = serializers.CharField()
    response_id = serializers.IntegerField(required=False, allow_null=True)


class SaveResponseSerializer(serializers.Serializer):
    question_answers = AnswerSerializer(many=True)
    form_typ = serializers.CharField()


class FormInitializationSerializer(serializers.Serializer):
    questions = QuestionSerializer(many=True)
    question_types = QuestionTypeSerializer(many=True)
    form_sub_types = FormSubTypeSerializer(many=True, required=False)
    flows = FlowSerializer(many=True, required=False)


class GraphTypeSerializer(serializers.Serializer):
    graph_typ = serializers.CharField()
    graph_nm = serializers.CharField()


class GraphSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    graph_typ = GraphTypeSerializer()
    name = serializers.CharField()
    active = serializers.CharField()


class GraphQuestionType(serializers.Serializer):
    graph_question_typ = serializers.CharField()
    graph_question_nm = serializers.CharField()
    question_types = QuestionTypeSerializer(many=True)


class GraphQuestion(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    graph = GraphSerializer()
    question = QuestionSerializer()
    graph_question_typ = GraphQuestionType()
    active = serializers.CharField()
