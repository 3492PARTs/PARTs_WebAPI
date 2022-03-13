from rest_framework import serializers
from api.api.scoutAdmin.serializers import ScoutFieldScheduleSerializer, ScoutPitScheduleSerializer


class EventUpdatedMessageSerializer(serializers.Serializer):
    event_name = serializers.CharField()
    first_match_time = serializers.CharField()
    event_key = serializers.CharField()


class EventUpdatedSerializer(serializers.Serializer):
    message_data = EventUpdatedMessageSerializer()
    message_type = serializers.CharField()
