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
    team_no = serializers.IntegerField()
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
    event_id = serializers.IntegerField()
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


class QuestionTypeSerializer(serializers.Serializer):
    question_typ = serializers.CharField()
    question_typ_nm = serializers.CharField()


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


class ScoutFieldScheduleSaveSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField(read_only=True)
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField()
    red_one_id = serializers.IntegerField()
    red_two_id = serializers.IntegerField()
    red_three_id = serializers.IntegerField()
    blue_one_id = serializers.IntegerField()
    blue_two_id = serializers.IntegerField()
    blue_three_id = serializers.IntegerField()
    void_ind = serializers.CharField(default='n')


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


class ScoutQuestionSubTypeSerializer(serializers.Serializer):
    sq_sub_typ = serializers.CharField()
    sq_sub_nm = serializers.CharField()
    sq_typ_id = serializers.CharField()


class QuestionOptionsSerializer(serializers.Serializer):
    q_opt_id = serializers.IntegerField(required=False, allow_null=True)
    sq_id = serializers.IntegerField(read_only=True)
    option = serializers.CharField()
    active = serializers.CharField()


class ScoutQuestionSerializer(serializers.Serializer):
    sq_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)

    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField()
    question_typ = serializers.CharField()
    question_typ_nm = serializers.CharField(required=False, allow_blank=True)
    sq_sub_typ = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sq_sub_nm = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sq_typ = serializers.CharField()

    questionoptions_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True)

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)



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
