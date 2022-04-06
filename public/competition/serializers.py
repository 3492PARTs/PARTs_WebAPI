from rest_framework import serializers

from scouting.admin.serializers import EventSerializer, MatchSerializer


class CompetitionInformationSerializer(serializers.Serializer):
    event = EventSerializer()
    matches = MatchSerializer(many=True, required=False)
