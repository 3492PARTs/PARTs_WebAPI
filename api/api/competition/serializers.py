from rest_framework import serializers

from api.api.scoutAdmin.serializers import EventSerializer, MatchSerializer


class CompetitionInformationSerializer(serializers.Serializer):
    event = EventSerializer()
    matches = MatchSerializer(many=True, required=False)
