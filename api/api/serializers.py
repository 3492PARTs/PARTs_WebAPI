from rest_framework import serializers
from .models import *
from api.auth.serializers import UserSerializer, AuthGroupSerializer, PhoneTypeSerializer


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
    answer = serializers.CharField(required=False)


class TeamSerializer(serializers.Serializer):
    team_no = serializers.CharField()
    team_nm = serializers.CharField()
    checked = serializers.BooleanField(required=False)


class ScoutAnswerSerializer(serializers.Serializer):
    scoutQuestions = ScoutQuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)


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


class ScoutScheduleSerializer(serializers.Serializer):
    scout_sch_id = serializers.IntegerField(required=False)
    user = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.IntegerField()
    sq_typ = serializers.CharField()
    sq_nm = serializers.CharField(required=False)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField(required=False)
    notify = serializers.CharField(required=False)


class ScoutQuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutQuestionType
        fields = '__all__'

class ScoutAdminInitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventSerializer(many=True)
    currentSeason = SeasonSerializer(required=False)
    currentEvent = EventSerializer(required=False)
    users = UserSerializer(many=True)
    userGroups = AuthGroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)
    fieldSchedule = ScoutScheduleSerializer(many=True)
    pitSchedule = ScoutScheduleSerializer(many=True)
    pastSchedule = ScoutScheduleSerializer(many=True)
    scoutQuestionType = ScoutQuestionTypeSerializer(many=True)

class ScoutPortalInitSerializer(serializers.Serializer):
    fieldSchedule = ScoutScheduleSerializer(many=True)
    pitSchedule = ScoutScheduleSerializer(many=True)
    pastSchedule = ScoutScheduleSerializer(many=True)


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestions = ScoutQuestionSerializer(many=True)


class ScoutAdminSaveUserSerializer(serializers.Serializer):
    user = UserSerializer(read_only=False)
    groups = AuthGroupSerializer(many=True)


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


class ScoutPitResultAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()


class ScoutPitResultsSerializer(serializers.Serializer):
    teamNo = serializers.CharField()
    teamNm = serializers.CharField()
    pic = serializers.CharField()
    results = ScoutPitResultAnswerSerializer(many=True)
