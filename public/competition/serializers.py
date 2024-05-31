from rest_framework import serializers


class EventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(read_only=True)
    season_id = serializers.IntegerField(read_only=True)
    event_nm = serializers.CharField()
    date_st = serializers.DateTimeField()
    date_end = serializers.DateTimeField()
    event_cd = serializers.CharField()
    event_url = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state_prov = serializers.CharField()
    postal_code = serializers.CharField()
    location_name = serializers.CharField()
    gmaps_url = serializers.CharField()
    webcast_url = serializers.CharField()
    timezone = serializers.CharField()
    current = serializers.CharField()
    competition_page_active = serializers.CharField()


class CompetitionLevelSerializer(serializers.Serializer):
    comp_lvl_typ = serializers.CharField()
    comp_lvl_typ_nm = serializers.CharField()
    comp_lvl_order = serializers.IntegerField()


class MatchSerializer(serializers.Serializer):
    match_id = serializers.CharField(read_only=True)
    event_id = serializers.IntegerField(read_only=True)
    match_number = serializers.IntegerField()
    red_score = serializers.IntegerField()
    blue_score = serializers.IntegerField()
    time = serializers.DateTimeField()
    blue_one = serializers.IntegerField()
    blue_two = serializers.IntegerField()
    blue_three = serializers.IntegerField()
    red_one = serializers.IntegerField()
    red_two = serializers.IntegerField()
    red_three = serializers.IntegerField()

    comp_level = CompetitionLevelSerializer(read_only=True)


class CompetitionInformationSerializer(serializers.Serializer):
    event = EventSerializer()
    matches = MatchSerializer(many=True, required=False)
