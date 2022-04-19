from rest_framework import serializers

from scouting.admin.serializers import ScoutFieldScheduleSerializer, ScoutQuestionSerializer
from scouting.models import Team


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


class ScoutFieldSerializer(serializers.Serializer):
    scoutQuestions = ScoutQuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)
    scoutFieldSchedule = ScoutFieldScheduleSerializer(required=False)


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
