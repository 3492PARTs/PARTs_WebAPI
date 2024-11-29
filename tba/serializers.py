from rest_framework import serializers


class AllianceSerializer(serializers.Serializer):
    score = serializers.CharField()
    teams = serializers.ListField(child=serializers.CharField())


class AlliancesSerializer(serializers.Serializer):
    blue = AllianceSerializer()
    red = AllianceSerializer()



class MatchSerializer(serializers.Serializer):
    comp_level = serializers.CharField()
    match_number = serializers.CharField()
    videos = serializers.ListSerializer(child=serializers.CharField())
    time_string = serializers.CharField()
    set_number = serializers.CharField()
    key = serializers.CharField()
    time = serializers.DateTimeField()
    score_breakdown = serializers.CharField()
    alliances = AlliancesSerializer()
    event_key = serializers.CharField()



class EventUpdatedMessageSerializer(serializers.Serializer):
    event_name = serializers.CharField()
    match = MatchSerializer()


class EventUpdatedSerializer(serializers.Serializer):
    message_data = EventUpdatedMessageSerializer()
    message_type = serializers.CharField()


class VerificationMessageDataSerializer(serializers.Serializer):
    verification_key = serializers.CharField()


class VerificationMessageSerializer(serializers.Serializer):
    message_data = VerificationMessageDataSerializer()
    message_type = serializers.CharField()