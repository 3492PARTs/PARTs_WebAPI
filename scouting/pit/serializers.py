from scouting.admin.serializers import *
from scouting.field.serializers import *
from scouting.models import ScoutPitAnswer


class InitSerializer(serializers.Serializer):
    scoutQuestions = ScoutQuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    comp_teams = TeamSerializer(many=True, required=False)


class ScoutAnswerSerializer(serializers.Serializer):
    scoutQuestions = ScoutQuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)


class ScoutPitResultAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_null=True)


class ScoutPitResultsSerializer(serializers.Serializer):
    teamNo = serializers.CharField()
    teamNm = serializers.CharField()
    pic = serializers.CharField()
    results = ScoutPitResultAnswerSerializer(many=True)


class PitTeamDataSerializer(serializers.Serializer):
    questions = ScoutQuestionSerializer(required=False, many=True)
    pic = serializers.CharField()
