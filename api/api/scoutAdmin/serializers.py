from rest_framework import serializers
from api.api.models import Season, Event, QuestionType, ScoutQuestionType
from api.auth.serializers import UserSerializer, GroupSerializer, PhoneTypeSerializer


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
    void_ind = serializers.CharField()

    st_time_str = serializers.CharField(required=False)
    end_time_str = serializers.CharField(required=False)


class ScoutQuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutQuestionType
        fields = '__all__'


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
    answer = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestions = ScoutQuestionSerializer(many=True)


class InitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventSerializer(many=True)
    currentSeason = SeasonSerializer(required=False)
    currentEvent = EventSerializer(required=False)
    users = UserSerializer(many=True)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)
    fieldSchedule = ScoutScheduleSerializer(many=True)
    pitSchedule = ScoutScheduleSerializer(many=True)
    pastSchedule = ScoutScheduleSerializer(many=True)
    scoutQuestionType = ScoutQuestionTypeSerializer(many=True)