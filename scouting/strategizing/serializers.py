from rest_framework import serializers

from form.serializers import QuestionSerializer, QuestionAggregateSerializer


class HistogramBinSerializer(serializers.Serializer):
    bin = serializers.CharField()
    count = serializers.IntegerField()

class HistogramSerializer(serializers.Serializer):
    label = serializers.CharField()
    bins = HistogramBinSerializer(many=True)

