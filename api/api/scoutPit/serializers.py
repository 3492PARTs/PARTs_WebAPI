from api.api.scoutAdmin.serializers import *
from api.api.scoutField.serializers import *


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
    answer = serializers.CharField()


class ScoutPitResultsSerializer(serializers.Serializer):
    teamNo = serializers.CharField()
    teamNm = serializers.CharField()
    pic = serializers.CharField()
    results = ScoutPitResultAnswerSerializer(many=True)
