from rest_framework import serializers
from .models import *


class QuestionOptionsSerializer(serializers.Serializer):
    q_opt_id = serializers.IntegerField()
    option = serializers.CharField()
    sfq = serializers.IntegerField()
    spq = serializers.IntegerField()
    active = serializers.CharField()
    void_ind = serializers.CharField()


class ScoutFieldQuestionSerializer(serializers.Serializer):
    sfq_id = serializers.IntegerField()
    season = serializers.IntegerField()
    question_typ = serializers.CharField()
    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField()
    void_ind = serializers.CharField()
    options = QuestionOptionsSerializer(many=True, allow_null=True)


class ScoutPitQuestionSerializer(serializers.Serializer):
    spq_id = serializers.IntegerField()
    season = serializers.IntegerField()
    question_typ = serializers.CharField()
    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField()
    void_ind = serializers.CharField()
    options = QuestionOptionsSerializer(many=True, allow_null=True)


class ScoutFieldQuestionAnswerSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    question = serializers.CharField()
    question_typ = serializers.CharField()
    season = serializers.IntegerField()
    sfq_id = serializers.IntegerField()
    void_ind = serializers.CharField()
    answer = serializers.CharField()


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'


class ScoutAdminInitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventSerializer(many=True)
    currentSeason = SeasonSerializer()
    currentEvent = EventSerializer()
    questionTypes = QuestionTypeSerializer(many=True)
    scoutFieldQuestions = ScoutFieldQuestionSerializer(many=True)
    scoutPitQuestions = ScoutPitQuestionSerializer(many=True)

