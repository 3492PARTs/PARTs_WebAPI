from rest_framework import serializers
from .models import *
from api.auth.models import AuthUser


class QuestionOptionsSerializer(serializers.Serializer):
    q_opt_id = serializers.IntegerField(required=False)
    option = serializers.CharField()
    sq = serializers.IntegerField(required=False)
    active = serializers.CharField(required=False)
    void_ind = serializers.CharField(required=False)


class ScoutQuestionSerializer(serializers.Serializer):
    sq_id = serializers.IntegerField(required=False)
    season = serializers.IntegerField(required=False)
    sq_typ = serializers.CharField(required=False)
    question_typ = serializers.CharField()
    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField(required=False)
    void_ind = serializers.CharField(required=False)
    options = QuestionOptionsSerializer(many=True)


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'


class ScoutAdminInitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventSerializer(many=True)
    currentSeason = SeasonSerializer()
    currentEvent = EventSerializer()
    users = UserSerializer(many=True)


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestions = ScoutQuestionSerializer(many=True)

