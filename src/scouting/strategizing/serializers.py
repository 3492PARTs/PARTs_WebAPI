from rest_framework import serializers

from form.serializers import QuestionSerializer, QuestionAggregateSerializer
from scouting.serializers import TeamSerializer


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


class TouchMapPointSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()


class TouchMapSerializer(serializers.Serializer):
    label = serializers.CharField()
    question = QuestionSerializer()
    points = TouchMapPointSerializer(many=True)


class DashboardGraphSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    graph_id = serializers.IntegerField()
    graph_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    graph_nm = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    graph_typ = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    x_scale_min = serializers.IntegerField()
    x_scale_max = serializers.IntegerField()
    y_scale_min = serializers.IntegerField()
    y_scale_max = serializers.IntegerField()
    order = serializers.IntegerField()
    active = serializers.CharField()


class DashboardViewTypeSerializer(serializers.Serializer):
    dash_view_typ = serializers.CharField()
    dash_view_nm = serializers.CharField()


class DashboardViewSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    dash_view_typ = DashboardViewTypeSerializer()
    teams = TeamSerializer(many=True)
    reference_team_id = serializers.IntegerField(required=False, allow_null=True)
    dashboard_graphs = DashboardGraphSerializer(many=True)
    name = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField()


class DashboardSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    active = serializers.CharField()
    dashboard_views = DashboardViewSerializer(many=True)
    default_dash_view_typ = DashboardViewTypeSerializer()
