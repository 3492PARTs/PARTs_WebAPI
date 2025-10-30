from rest_framework import serializers

from form.serializers import QuestionSerializer
from scouting.serializers import EventSerializer, SeasonSerializer, TeamSerializer


class PitResponseAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_null=True)


class PitImageTypeSerializer(serializers.Serializer):
    pit_image_typ = serializers.CharField()
    pit_image_nm = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class PitImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    img_url = serializers.CharField()
    img_title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    pit_image_typ = PitImageTypeSerializer()
    default = serializers.BooleanField()


class PitResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()
    pics = PitImageSerializer(many=True, required=False)
    responses = PitResponseAnswerSerializer(many=True)


class PitResponsesSerializer(serializers.Serializer):
    teams = PitResponseSerializer(many=True)
    current_season = SeasonSerializer()
    current_event = EventSerializer()


class PitTeamDataSerializer(serializers.Serializer):
    response_id = serializers.IntegerField(required=False)
    questions = QuestionSerializer(required=False, many=True)
    pics = PitImageSerializer(many=True, required=False)
