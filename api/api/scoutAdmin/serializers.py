from rest_framework import serializers
from api.api.models import CompetitionLevel, Match, ScoutFieldSchedule, ScoutPitSchedule, ScoutQuestionSubType, Season, Event, QuestionType, ScoutQuestionType
from api.auth.serializers import UserSerializer, GroupSerializer, PhoneTypeSerializer


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class CompetitionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionLevel
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    comp_level = CompetitionLevelSerializer(read_only=True)

    class Meta:
        model = Match
        fields = '__all__'


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'


class ScoutFieldScheduleSerializer(serializers.ModelSerializer):
    scout_field_sch_id = serializers.IntegerField(
        required=False, allow_null=True)
    red_one = UserSerializer(required=False, allow_null=True, read_only=True)
    red_two = UserSerializer(required=False, allow_null=True, read_only=True)
    red_three = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_one = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_two = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_three = UserSerializer(
        required=False, allow_null=True, read_only=True)

    class Meta:
        model = ScoutFieldSchedule
        fields = '__all__'


class ScoutFieldScheduleSaveSerializer(serializers.ModelSerializer):
    scout_field_sch_id = serializers.IntegerField(
        required=False, allow_null=True)

    class Meta:
        model = ScoutFieldSchedule
        fields = '__all__'


class ScoutPitScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutPitSchedule
        fields = '__all__'


class ScoutQuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutQuestionType
        fields = '__all__'


class ScoutQuestionSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutQuestionSubType
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
    sq_sub_typ = serializers.CharField(required=False, allow_null=True)
    question_typ = serializers.CharField()
    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField(required=False)
    void_ind = serializers.CharField(required=False)
    options = QuestionOptionsSerializer(many=True)
    answer = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestionSubTypes = ScoutQuestionSubTypeSerializer(
        many=True, required=False)
    scoutQuestions = ScoutQuestionSerializer(many=True)


class InitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventSerializer(many=True)
    currentSeason = SeasonSerializer(required=False)
    currentEvent = EventSerializer(required=False)
    users = UserSerializer(many=True)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)
    fieldSchedule = ScoutFieldScheduleSerializer(many=True)
    pitSchedule = ScoutPitScheduleSerializer(many=True)
    #pastSchedule = ScoutScheduleSerializer(many=True)
    scoutQuestionType = ScoutQuestionTypeSerializer(many=True)
