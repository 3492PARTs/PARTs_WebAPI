from rest_framework import serializers

from form.serializers import QuestionSerializer


class SeasonSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(read_only=True)
    season = serializers.CharField()
    current = serializers.CharField()


class EventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=False)
    season_id = serializers.IntegerField()
    event_nm = serializers.CharField()
    date_st = serializers.DateTimeField()
    date_end = serializers.DateTimeField()
    event_cd = serializers.CharField()
    event_url = serializers.CharField(required=False)
    address = serializers.CharField()
    city = serializers.CharField()
    state_prov = serializers.CharField()
    postal_code = serializers.CharField()
    location_name = serializers.CharField()
    gmaps_url = serializers.CharField(required=False)
    webcast_url = serializers.CharField(required=False)
    timezone = serializers.CharField()
    current = serializers.CharField()
    competition_page_active = serializers.CharField()
    void_ind = serializers.CharField(default="n")


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)


class InitSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    comp_teams = TeamSerializer(many=True, required=False)


class ScoutAnswerSerializer(serializers.Serializer):
    scoutQuestions = QuestionSerializer(many=True)
    teams = TeamSerializer(many=True, required=False)
    team = serializers.CharField(required=False)


class ScoutPitResponseAnswerSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_null=True)


class ScoutPitImageSerializer(serializers.Serializer):
    scout_pit_img_id = serializers.IntegerField(required=False)
    pic = serializers.CharField()
    default = serializers.BooleanField()


class ScoutPitResponseSerializer(serializers.Serializer):
    scout_pit_id = serializers.IntegerField()
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()
    pics = ScoutPitImageSerializer(many=True, required=False)
    responses = ScoutPitResponseAnswerSerializer(many=True)


class ScoutPitResponsesSerializer(serializers.Serializer):
    teams = ScoutPitResponseSerializer(many=True)
    current_season = SeasonSerializer()
    current_event = EventSerializer()


class PitTeamDataSerializer(serializers.Serializer):
    response_id = serializers.IntegerField(required=False)
    questions = QuestionSerializer(required=False, many=True)
    pics = ScoutPitImageSerializer(many=True, required=False)
