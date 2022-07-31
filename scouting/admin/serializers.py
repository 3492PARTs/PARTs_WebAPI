from rest_framework import serializers
from scouting.models import CompetitionLevel, Match, QuestionOptions, ScoutFieldSchedule, ScoutPitAnswer, ScoutPitSchedule, ScoutQuestion, ScoutQuestionSubType, Season, Event, QuestionType, ScoutQuestionType
from user.serializers import UserSerializer, GroupSerializer, PhoneTypeSerializer
from scouting.models import Team


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    checked = serializers.BooleanField(required=False)

    class Meta:
        model = Team
        fields = '__all__'
        extra_kwargs = {
            'team_no': {
                'validators': [],
            },
        }


class Team2Serializer(serializers.ModelSerializer):
    # this is bc i need a default checked team serializer
    checked = serializers.BooleanField(default=True)

    class Meta:
        model = Team
        fields = '__all__'
        extra_kwargs = {
            'team_no': {
                'validators': [],
            },
        }


class EventSerializer(serializers.ModelSerializer):
    # TODO Why did i do this??????? Why is there only one team here?
    team_no = TeamSerializer(required=False)
    checked = serializers.BooleanField(required=False)

    class Meta:
        model = Event
        fields = '__all__'


class Event2Serializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class Event3Serializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(
        required=False, allow_null=True)
    team_no = Team2Serializer(required=False, many=True)

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'event_cd': {
                'validators': [],
            },
        }


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


class QuestionOptionsSerializer(serializers.ModelSerializer):
    q_opt_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = QuestionOptions
        fields = '__all__'
        extra_kwargs = {'sq': {'required': False}}


class ScoutQuestionSerializer(serializers.ModelSerializer):
    sq_id = serializers.IntegerField(required=False, allow_null=True)
    season = serializers.CharField(required=False, allow_null=True)
    questionoptions_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True)

    answer = serializers.CharField(required=False, allow_null=True)

    answer = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = ScoutQuestion
        fields = '__all__'


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestionSubTypes = ScoutQuestionSubTypeSerializer(
        many=True, required=False)
    scoutQuestions = ScoutQuestionSerializer(many=True)


class EventToTeamsSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    teams = TeamSerializer(many=True)


class InitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = Event3Serializer(many=True)
    currentSeason = SeasonSerializer(required=False)
    currentEvent = Event2Serializer(required=False)
    users = UserSerializer(many=True)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)
    fieldSchedule = ScoutFieldScheduleSerializer(many=True)
    pitSchedule = ScoutPitScheduleSerializer(many=True)
    #pastSchedule = ScoutScheduleSerializer(many=True)
    scoutQuestionType = ScoutQuestionTypeSerializer(many=True)
    teams = TeamSerializer(many=True)
