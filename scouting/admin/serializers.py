from django.db.models import Q
from rest_framework import serializers

from form.serializers import (
    FormSubTypeSerializer,
    QuestionTypeSerializer,
    QuestionSerializer,
    FormTypeSerializer,
)
from scouting.models import Team, Event, FieldSchedule, Schedule
from scouting.serializers import EventSerializer, SeasonSerializer, TeamSerializer
from user.serializers import UserSerializer, PhoneTypeSerializer, GroupSerializer


class TeamCreateSerializer(serializers.Serializer):
    team_no = serializers.CharField()
    team_nm = serializers.CharField()
    void_ind = serializers.CharField(default="n")

    def create(self, validated_data):
        t = Team(
            team_no=validated_data["team_no"],
            team_nm=validated_data["team_nm"],
            void_ind=validated_data["void_ind"],
        )
        t.save()
        return t


class ScoutFieldScheduleSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField()
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notification1 = serializers.BooleanField(read_only=True)
    notification2 = serializers.BooleanField(read_only=True)
    notification3 = serializers.BooleanField(read_only=True)

    red_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_three_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_three_id = UserSerializer(required=False, allow_null=True, read_only=True)

    red_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_three_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_three_check_in = serializers.DateTimeField(required=False, allow_null=True)

    scouts = serializers.CharField(read_only=True)


class ScoutFieldScheduleSaveSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField(required=False, allow_null=True)
    event_id = serializers.IntegerField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField(default="n")
    red_one_id = serializers.IntegerField(allow_null=True)
    red_two_id = serializers.IntegerField(allow_null=True)
    red_three_id = serializers.IntegerField(allow_null=True)
    blue_one_id = serializers.IntegerField(allow_null=True)
    blue_two_id = serializers.IntegerField(allow_null=True)
    blue_three_id = serializers.IntegerField(allow_null=True)
    void_ind = serializers.CharField(default="n")


class ScheduleSaveSerializer(serializers.Serializer):
    sch_id = serializers.IntegerField(required=False, allow_null=True)
    sch_typ = serializers.CharField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.BooleanField(default=False)
    user = serializers.IntegerField(allow_null=True)
    void_ind = serializers.CharField(default="n")


class ScoutPitScheduleSerializer(serializers.Serializer):
    scout_pit_sch_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField()
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField()


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestionSubTypes = FormSubTypeSerializer(many=True, required=False)
    scoutQuestions = QuestionSerializer(many=True)


class EventToTeamsSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    teams = TeamSerializer(many=True)


class ScoutFieldSerializer(serializers.Serializer):
    scout_field_id = serializers.IntegerField()
    event = serializers.IntegerField()
    team_no = serializers.IntegerField()
    user = serializers.IntegerField()
    time = serializers.DateTimeField()
    match = serializers.IntegerField()


class InitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    # events = EventTeamSerializer(many=True)
    currentSeason = SeasonSerializer(required=False)
    currentEvent = EventSerializer(required=False)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)
    fieldSchedule = ScoutFieldScheduleSerializer(many=True)
    # pitSchedule = ScoutPitScheduleSerializer(many=True)
    # pastSchedule = ScoutScheduleSerializer(many=True)
    scoutQuestionType = FormTypeSerializer(many=True)
    teams = TeamSerializer(many=True)


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


class ScoutingUserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    under_review = serializers.BooleanField(required=False)


class UserScoutingUserInfoSerializer(serializers.Serializer):
    user = UserSerializer()
    user_info = ScoutingUserInfoSerializer()
