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


class DashboardGraphSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    graph_id = serializers.IntegerField()
    graph_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    graph_nm = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    order = serializers.IntegerField()
    active = serializers.CharField()


class DashboardActiveTeamSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, allow_null=True)
    team_id = serializers.IntegerField(required=False, allow_null=True)
    reference_team_id = serializers.IntegerField(required=False, allow_null=True)


class DashboardSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    active = serializers.CharField()
    dashboard_graphs = DashboardGraphSerializer(many=True)
    active_team = DashboardActiveTeamSerializer(required=False)