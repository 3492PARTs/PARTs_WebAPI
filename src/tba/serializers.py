from rest_framework import serializers


class MatchVideoSerializer(serializers.Serializer):
    type = serializers.CharField()
    key = serializers.CharField()


class AllianceSerializer(serializers.Serializer):
    score = serializers.CharField()
    team_keys = serializers.ListField(child=serializers.CharField())


class AlliancesSerializer(serializers.Serializer):
    blue = AllianceSerializer()
    red = AllianceSerializer()


class TBAMatchSerializer(serializers.Serializer):
    key = serializers.CharField()
    event_key = serializers.CharField()
    comp_level = serializers.CharField()
    set_number = serializers.CharField()
    match_number = serializers.CharField()
    videos = MatchVideoSerializer(many=True)
    time = serializers.IntegerField()
    # score_breakdown = serializers.CharField()
    alliances = AlliancesSerializer()


class EventUpdatedMessageSerializer(serializers.Serializer):
    event_key = serializers.CharField()
    match_key = serializers.CharField()
    event_name = serializers.CharField()
    match = TBAMatchSerializer()


class EventUpdatedSerializer(serializers.Serializer):
    message_data = EventUpdatedMessageSerializer()
    message_type = serializers.CharField()


class ScheduleUpdatedMessageSerializer(serializers.Serializer):
    event_key = serializers.CharField()
    event_name = serializers.CharField()
    # first_match_time = serializers.IntegerField()


class ScheduleUpdatedSerializer(serializers.Serializer):
    message_data = ScheduleUpdatedMessageSerializer()
    message_type = serializers.CharField()


class VerificationMessageDataSerializer(serializers.Serializer):
    verification_key = serializers.CharField()


class VerificationMessageSerializer(serializers.Serializer):
    message_data = VerificationMessageDataSerializer()
    message_type = serializers.CharField()
