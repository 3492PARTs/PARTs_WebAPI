from rest_framework import serializers

from form.serializers import QuestionSerializer, QuestionAggregateSerializer


class HistogramBinSerializer(serializers.Serializer):
    bin = serializers.CharField()
    count = serializers.IntegerField()

class HistogramSerializer(serializers.Serializer):
    label = serializers.CharField()
    bins = HistogramBinSerializer(many=True)


class PlotPointSerializer(serializers.Serializer):
    point = serializers.FloatField()
    time = serializers.DateTimeField()


class PlotSerializer(serializers.Serializer):
    label = serializers.CharField()
    points = PlotPointSerializer(many=True)

class BoxAndWhiskerPlotSerializer(serializers.Serializer):
    label = serializers.CharField()
    q1 = serializers.FloatField()
    q2 = serializers.FloatField()
    q3 = serializers.FloatField()
    min = serializers.FloatField()
    max = serializers.FloatField()