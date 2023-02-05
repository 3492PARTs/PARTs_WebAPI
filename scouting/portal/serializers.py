from rest_framework import serializers
from scouting.admin.serializers import ScoutFieldScheduleSerializer, ScoutPitScheduleSerializer


class InitSerializer(serializers.Serializer):
    fieldSchedule = ScoutFieldScheduleSerializer(many=True, required=False)
    pitSchedule = ScoutPitScheduleSerializer(many=True, required=False)
    #pastSchedule = ScoutScheduleSerializer(many=True)