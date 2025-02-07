from rest_framework import serializers

from form.serializers import QuestionSerializer, QuestionAggregateSerializer


class HistogramBinSerializer(serializers.Serializer):
    bin = serializers.IntegerField()
    width = serializers.IntegerField()
    count = serializers.IntegerField()

class HistogramSerializer(serializers.Serializer):
    label = serializers.CharField()
    bins = HistogramBinSerializer(many=True)

