from django.db.models import Q
from rest_framework import serializers

from scouting.models import Schedule, Event
from scouting.serializers import (
    ScheduleSerializer,
    ScheduleTypeSerializer,
    ScoutFieldScheduleSerializer,
)
from user.serializers import UserSerializer


class ScheduleByTypeSerializer(serializers.Serializer):
    sch_typ = ScheduleTypeSerializer()
    sch = ScheduleSerializer(many=True, required=False)


class InitSerializer(serializers.Serializer):
    fieldSchedule = ScoutFieldScheduleSerializer(many=True, required=False)
    schedule = ScheduleSerializer(many=True, required=False)
    allFieldSchedule = ScoutFieldScheduleSerializer(many=True, required=False)
    allSchedule = ScheduleByTypeSerializer(many=True, required=False)
    users = UserSerializer(many=True, required=False)
    scheduleTypes = ScheduleTypeSerializer(many=True, required=False)
