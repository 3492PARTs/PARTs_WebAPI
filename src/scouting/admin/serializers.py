from rest_framework import serializers

from form.serializers import (
    FormSubTypeSerializer,
    QuestionTypeSerializer,
    QuestionSerializer,
    FormTypeSerializer,
)
from scouting.models import Team
from scouting.serializers import (
    EventSerializer,
    SeasonSerializer,
    TeamSerializer,
    ScoutFieldScheduleSerializer,
)
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


class ScoutFieldScheduleSaveSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
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
    id = serializers.IntegerField(required=False, allow_null=True)
    sch_typ = serializers.CharField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.BooleanField(default=False)
    user = serializers.IntegerField(allow_null=True)
    void_ind = serializers.CharField(default="n")


class EventToTeamsSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    teams = TeamSerializer(many=True)


class ScoutingUserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    user = UserSerializer()
    under_review = serializers.BooleanField(required=False)
    group_leader = serializers.BooleanField(required=False)
    eliminate_results = serializers.BooleanField(required=False)
