from rest_framework import serializers

from api.api.scoutAdmin.serializers import ScoutQuestionSerializer


class TeamSerializer(serializers.Serializer):
    team_no = serializers.CharField()
    team_nm = serializers.CharField()
    checked = serializers.BooleanField(required=False)


class ScoutFieldSerializer(serializers.Serializer):
    scoutQuestions = ScoutQuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)


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
