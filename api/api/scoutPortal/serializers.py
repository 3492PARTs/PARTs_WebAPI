from rest_framework import serializers
from api.api.scoutAdmin.serializers import ScoutScheduleSerializer


class InitSerializer(serializers.Serializer):
    fieldSchedule = ScoutScheduleSerializer(many=True)
    pitSchedule = ScoutScheduleSerializer(many=True)
    pastSchedule = ScoutScheduleSerializer(many=True)
