from rest_framework import serializers

from form.serializers import (
    QuestionSerializer, QuestionAnswerSerializer,
)
from scouting.serializers import EventSerializer, SeasonSerializer, MatchSerializer
from user.serializers import UserSerializer


class SaveScoutFieldSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    team = serializers.CharField()
    match = serializers.CharField(required=False)


class ScoutColSerializer(serializers.Serializer):
    PropertyName = serializers.CharField()
    ColLabel = serializers.CharField()
    Width = serializers.CharField(required=False)
    order = serializers.CharField()


class ScoutResultAnswerSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance


class ScoutFieldSerializer(serializers.Serializer):
    scout_field_id = serializers.IntegerField()
    # response = serializers.IntegerField()
    # event = serializers.IntegerField()
    # team_no = serializers.IntegerField()
    # user = serializers.IntegerField()
    # time = serializers.DateTimeField()
    # match = serializers.IntegerField()
    # void_ind = serializers.CharField()


class ScoutFieldResultsSerializer(serializers.Serializer):
    scoutCols = ScoutColSerializer(many=True)
    scoutAnswers = ScoutResultAnswerSerializer(many=True)
    current_season = SeasonSerializer()
    current_event = EventSerializer()
    removed_responses = ScoutFieldSerializer(many=True)

class FieldResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    match = MatchSerializer(required=False)
    user = UserSerializer()
    time = serializers.DateTimeField()
    answers = QuestionAnswerSerializer(many=True)
    display_value = serializers.CharField()