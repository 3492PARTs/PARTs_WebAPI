from rest_framework import serializers
from api.api.scoutAdmin.serializers import ScoutFieldScheduleSerializer, ScoutPitScheduleSerializer


class InitSerializer(serializers.Serializer):
    fieldSchedule = ScoutFieldScheduleSerializer(many=True)
    pitSchedule = ScoutPitScheduleSerializer(many=True)
    #pastSchedule = ScoutScheduleSerializer(many=True)
