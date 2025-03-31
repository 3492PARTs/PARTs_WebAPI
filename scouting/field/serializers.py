from rest_framework import serializers

from form.serializers import (
    QuestionSerializer,
    AnswerSerializer,
)
from scouting.serializers import EventSerializer, SeasonSerializer, MatchSerializer
from user.serializers import UserSerializer


class ColSerializer(serializers.Serializer):
    PropertyName = serializers.CharField()
    ColLabel = serializers.CharField()
    Width = serializers.CharField(required=False)
    order = serializers.CharField()


class FieldResponseAnswerSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance


class FieldResponsesSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    previous = serializers.IntegerField()
    next = serializers.IntegerField()
    # scoutCols = ColSerializer(many=True)
    scoutAnswers = FieldResponseAnswerSerializer(many=True)
    current_season = SeasonSerializer()
    current_event = EventSerializer()
    removed_responses = serializers.ListField()


class FieldResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    match = MatchSerializer(required=False)
    user = UserSerializer()
    time = serializers.DateTimeField()
    answers = AnswerSerializer(many=True)
    display_value = serializers.CharField()
