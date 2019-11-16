from rest_framework import serializers
from .models import *


class ScoutFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutFieldQuestion
        fields = '__all__'

class ScoutFieldQuestionAnswerSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    question = serializers.CharField()
    question_typ = serializers.CharField()
    season = serializers.IntegerField()
    sfq_id = serializers.IntegerField()
    void_ind = serializers.CharField()
    answer = serializers.CharField()


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'
