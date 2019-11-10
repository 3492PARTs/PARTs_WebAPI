from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *
"""
# Main query params serializers
class DataPointSerialiser(serializers.Serializer):
    data = serializers.ListField()
    label = serializers.CharField()

class DataSetSerializer(serializers.Serializer):
    sens = serializers.CharField()
    #values = serializers.ListField()
    lineChartData = DataPointSerialiser(many=True)
    lineChartLabels = serializers.ListField()


class NodeSerializer(serializers.Serializer):
    node_id = serializers.CharField(max_length=12)
    node_nm = serializers.CharField(max_length=100)
    checked = serializers.BooleanField()
    dataset = DataSetSerializer(many=True, required=False)

    class Meta:
        model = Node


class BaseStationSerializer(serializers.Serializer):
    base_id = serializers.CharField(max_length=16)
    base_nm = serializers.CharField(max_length=100)
    checked = serializers.BooleanField()
    nodes = NodeSerializer(many=True)

    class Meta:
        model = BaseStation


class LocationSerializer(serializers.Serializer):
    loc_id = serializers.IntegerField()
    loc_nm = serializers.CharField(max_length=500)
    checked = serializers.BooleanField()
    bases = BaseStationSerializer(many=True)

    class Meta:
        model = Location


class MainQuerySerializer(serializers.Serializer):
    locs = LocationSerializer(many=True)
    date_st = serializers.CharField()
    date_end = serializers.CharField()

# Inserting data serializers

class InsertSensDataSerializer(serializers.Serializer):
    sens_typ_cd = serializers.CharField(max_length=100, required=True)
    data = serializers.FloatField(required=True)


class InsertDataSerializer(serializers.Serializer):
    base_id = serializers.CharField(max_length=16)
    node_id = serializers.CharField(max_length=12)
    dataset = InsertSensDataSerializer(many=True, required=False)
    error_list = serializers.ListField(required=False)"""



