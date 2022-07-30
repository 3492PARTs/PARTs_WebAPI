from rest_framework import serializers

from scouting.admin.serializers import Event2Serializer, MatchSerializer


class CompetitionInformationSerializer(serializers.Serializer):
    event = Event2Serializer()
    matches = MatchSerializer(many=True, required=False)
