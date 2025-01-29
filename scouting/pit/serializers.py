from rest_framework import serializers

from form.serializers import QuestionSerializer
from scouting.serializers import EventSerializer, SeasonSerializer, TeamSerializer


class InitSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    comp_teams = TeamSerializer(many=True, required=False)


class ScoutAnswerSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)


class ScoutPitResponseAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_null=True)


class ScoutPitImageSerializer(serializers.Serializer):
    scout_pit_img_id = serializers.IntegerField(required=False)
    pic = serializers.CharField()
    default = serializers.BooleanField()


class ScoutPitResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()
    pics = ScoutPitImageSerializer(many=True, required=False)
    responses = ScoutPitResponseAnswerSerializer(many=True)


class ScoutPitResponsesSerializer(serializers.Serializer):
    teams = ScoutPitResponseSerializer(many=True)
    current_season = SeasonSerializer()
    current_event = EventSerializer()


class PitTeamDataSerializer(serializers.Serializer):
    response_id = serializers.IntegerField(required=False)
    questions = QuestionSerializer(required=False, many=True)
    pics = ScoutPitImageSerializer(many=True, required=False)
