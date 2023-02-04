from rest_framework import serializers
from scouting.models import CompetitionLevel, Match, QuestionOptions, ScoutFieldSchedule, ScoutPitAnswer, ScoutPitSchedule, ScoutQuestion, ScoutQuestionSubType, Season, Event, QuestionType, ScoutQuestionType
from scouting.models import Team


class SeasonSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(read_only=True)
    season = serializers.CharField()
    current = serializers.CharField()


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField(read_only=True)
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)



class TeamCheckedSerializer(serializers.Serializer):
    team_no = serializers.IntegerField(read_only=True)
    team_nm = serializers.CharField()

    # this is bc I need a default checked team serializer
    checked = serializers.BooleanField(default=True)


class TeamCreateSerializer(serializers.Serializer):
    team_no = serializers.CharField()
    team_nm = serializers.CharField()
    void_ind = serializers.CharField(default='n')

    def create(self, validated_data):
        t = Team(team_no=validated_data['team_no'], team_nm=validated_data['team_nm'], void_ind=validated_data['void_ind'])
        t.save()
        return t


'''
class EventSerializer(serializers.ModelSerializer):
    # TODO Why did i do this??????? Why is there only one team here?
    team_no = TeamSerializer(required=False)
    checked = serializers.BooleanField(required=False)

    class Meta:
        model = Event
        fields = '__all__'
'''

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


class EventCreateSerializer(serializers.ModelSerializer):
    team_no = serializers.ListField(required=False)

    class Meta:
        model = Event
        fields = '__all__'


class EventTeamSerializer(serializers.Serializer):
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

    team_no = TeamCheckedSerializer(required=False, many=True)



class CompetitionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionLevel
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    comp_level = CompetitionLevelSerializer(read_only=True)

    class Meta:
        model = Match
        fields = '__all__'


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    content_type_id = serializers.IntegerField(read_only=True)
    codename = serializers.CharField()


class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    permissions = PermissionSerializer(many=True, required=False)


class PhoneTypeSerializer(serializers.Serializer):
    phone_type_id = serializers.IntegerField(read_only=True)
    carrier = serializers.CharField()
    phone_type = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField()

    groups = GroupSerializer(many=True, required=False)
    phone_type = PhoneTypeSerializer(required=False, allow_null=True)
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)


class ScoutFieldScheduleSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField(read_only=True)
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField()

    red_one = UserSerializer(required=False, allow_null=True, read_only=True)
    red_two = UserSerializer(required=False, allow_null=True, read_only=True)
    red_three = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_one = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_two = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_three = UserSerializer(
        required=False, allow_null=True, read_only=True)


class ScoutFieldScheduleSaveSerializer(serializers.ModelSerializer):
    scout_field_sch_id = serializers.IntegerField(
        required=False, allow_null=True)

    class Meta:
        model = ScoutFieldSchedule
        fields = '__all__'


class ScoutPitScheduleSerializer(serializers.Serializer):
    scout_pit_sch_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField()
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField()



class ScoutQuestionTypeSerializer(serializers.Serializer):
    sq_typ = serializers.CharField(read_only=True)
    sq_nm = serializers.CharField()


class ScoutQuestionSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutQuestionSubType
        fields = '__all__'


class QuestionOptionsSerializer(serializers.ModelSerializer):
    q_opt_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = QuestionOptions
        fields = '__all__'
        extra_kwargs = {'sq': {'required': False}}


class ScoutQuestionSerializer(serializers.ModelSerializer):
    sq_id = serializers.IntegerField(read_only=True)
    season = serializers.CharField(required=False, allow_null=True)
    questionoptions_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True)

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = ScoutQuestion
        fields = '__all__'


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestionSubTypes = ScoutQuestionSubTypeSerializer(
        many=True, required=False)
    scoutQuestions = ScoutQuestionSerializer(many=True)


class EventToTeamsSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    teams = TeamSerializer(many=True)


class InitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    events = EventTeamSerializer(many=True)
    currentSeason = SeasonSerializer(required=False)
    currentEvent = EventSerializer(required=False)
    users = UserSerializer(many=True)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)
    fieldSchedule = ScoutFieldScheduleSerializer(many=True)
    pitSchedule = ScoutPitScheduleSerializer(many=True)
    #pastSchedule = ScoutScheduleSerializer(many=True)
    scoutQuestionType = ScoutQuestionTypeSerializer(many=True)
    teams = TeamSerializer(many=True)
