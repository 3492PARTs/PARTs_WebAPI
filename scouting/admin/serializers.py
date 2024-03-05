from rest_framework import serializers
from scouting.models import Team, Event, ScoutFieldSchedule


class SeasonSerializer(serializers.Serializer):
    season_id = serializers.IntegerField(read_only=True)
    season = serializers.CharField()
    current = serializers.CharField()


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
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
        t = Team(team_no=validated_data['team_no'], team_nm=validated_data['team_nm'],
                 void_ind=validated_data['void_ind'])
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
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        e = Event(season_id=validated_data['season_id'], event_nm=validated_data['event_nm'],
                  date_st=validated_data['date_st'], event_cd=validated_data['event_cd'],
                  event_url=validated_data.get('event_url', None), address=validated_data['address'],
                  city=validated_data['city'], state_prov=validated_data['state_prov'],
                  postal_code=validated_data['postal_code'], location_name=validated_data['location_name'],
                  gmaps_url=validated_data.get('gmaps_url', None), webcast_url=validated_data.get('webcast_url', None),
                  date_end=validated_data['date_end'], timezone=validated_data['timezone'],
                  current=validated_data['current'], competition_page_active=validated_data['competition_page_active'],
                  void_ind=validated_data['void_ind'])
        e.save()
        return e

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
    void_ind = serializers.CharField(default='n')


"""
class EventCreateSerializer(serializers.ModelSerializer):
    team_no = serializers.ListField(required=False)

    class Meta:
        model = Event
        fields = '__all__'
"""


class EventTeamSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    season_id = serializers.IntegerField(read_only=True)
    event_nm = serializers.CharField()
    date_st = serializers.DateTimeField()
    date_end = serializers.DateTimeField()
    event_cd = serializers.CharField()
    event_url = serializers.CharField(allow_null=True)
    address = serializers.CharField()
    city = serializers.CharField()
    state_prov = serializers.CharField()
    postal_code = serializers.CharField()
    location_name = serializers.CharField()
    gmaps_url = serializers.CharField(allow_null=True)
    webcast_url = serializers.CharField(allow_null=True)
    timezone = serializers.CharField()
    current = serializers.CharField()
    competition_page_active = serializers.CharField()

    team_no = TeamCheckedSerializer(required=False, many=True)


"""
class CompetitionLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionLevel
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    comp_level = CompetitionLevelSerializer(read_only=True)

    class Meta:
        model = Match
        fields = '__all__'
"""


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
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)
    carrier = serializers.CharField()
    phone_type = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    phone = serializers.CharField(required=False, allow_null=True)
    discord_user_id = serializers.CharField(required=False, allow_null=True)

    groups = GroupSerializer(many=True, required=False)
    phone_type = PhoneTypeSerializer(required=False, allow_null=True)
    phone_type_id = serializers.IntegerField(required=False, allow_null=True)


class ScoutFieldScheduleSerializer(serializers.Serializer):
    scout_field_sch_id = serializers.IntegerField()
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notification1 = serializers.BooleanField(read_only=True)
    notification2 = serializers.BooleanField(read_only=True)
    notification3 = serializers.BooleanField(read_only=True)

    red_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    red_three_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_one_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_two_id = UserSerializer(required=False, allow_null=True, read_only=True)
    blue_three_id = UserSerializer(required=False, allow_null=True, read_only=True)

    red_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    red_three_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_one_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_two_check_in = serializers.DateTimeField(required=False, allow_null=True)
    blue_three_check_in = serializers.DateTimeField(required=False, allow_null=True)

    scouts = serializers.CharField(read_only=True)


class ScoutFieldScheduleSaveSerializer(serializers.Serializer):
    def create(self, validated_data):
        sfs = ScoutFieldSchedule(event_id=validated_data['event_id'], st_time=validated_data['st_time'],
                                 end_time=validated_data['end_time'],
                                 red_one_id=validated_data.get('red_one_id', None),
                                 red_two_id=validated_data.get('red_two_id', None),
                                 red_three_id=validated_data.get('red_three_id', None),
                                 blue_one_id=validated_data.get('blue_one_id', None),
                                 blue_two_id=validated_data.get('blue_two_id', None),
                                 blue_three_id=validated_data.get('blue_three_id', None),
                                 void_ind=validated_data['void_ind'])
        sfs.save()
        return sfs

    scout_field_sch_id = serializers.IntegerField(required=False, allow_null=True)
    event_id = serializers.IntegerField()
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField(default='n')
    red_one_id = serializers.IntegerField(allow_null=True)
    red_two_id = serializers.IntegerField(allow_null=True)
    red_three_id = serializers.IntegerField(allow_null=True)
    blue_one_id = serializers.IntegerField(allow_null=True)
    blue_two_id = serializers.IntegerField(allow_null=True)
    blue_three_id = serializers.IntegerField(allow_null=True)
    void_ind = serializers.CharField(default='n')


class ScoutPitScheduleSerializer(serializers.Serializer):
    scout_pit_sch_id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField()
    event_id = serializers.IntegerField(read_only=True)
    st_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    notified = serializers.CharField()


class FormTypeSerializer(serializers.Serializer):
    form_typ = serializers.CharField(read_only=True)
    form_nm = serializers.CharField()


class FormSubTypeSerializer(serializers.Serializer):
    form_sub_typ = serializers.CharField()
    form_sub_nm = serializers.CharField()
    form_typ_id = serializers.CharField()


class QuestionOptionsSerializer(serializers.Serializer):
    question_opt_id = serializers.IntegerField(required=False, allow_null=True)
    question_id = serializers.IntegerField(read_only=True)
    option = serializers.CharField()
    active = serializers.CharField()


class QuestionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=False, allow_null=True)
    season_id = serializers.IntegerField(read_only=True)

    question = serializers.CharField()
    order = serializers.IntegerField()
    active = serializers.CharField()
    question_typ = serializers.CharField()
    question_typ_nm = serializers.CharField(required=False, allow_blank=True)
    form_sub_typ = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_sub_nm = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    form_typ = serializers.CharField()
    display_value = serializers.CharField(read_only=True)

    questionoptions_set = QuestionOptionsSerializer(
        required=False, allow_null=True, many=True)

    answer = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class ScoutAdminQuestionInitSerializer(serializers.Serializer):
    questionTypes = QuestionTypeSerializer(many=True)
    scoutQuestionSubTypes = FormSubTypeSerializer(
        many=True, required=False)
    scoutQuestions = QuestionSerializer(many=True)


class EventToTeamsSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    teams = TeamSerializer(many=True)


class ScoutFieldSerializer(serializers.Serializer):
    scout_field_id = serializers.IntegerField()
    event = serializers.IntegerField()
    team_no = serializers.IntegerField()
    user = serializers.IntegerField()
    time = serializers.DateTimeField()
    match = serializers.IntegerField()


class InitSerializer(serializers.Serializer):
    seasons = SeasonSerializer(many=True)
    #events = EventTeamSerializer(many=True)
    currentSeason = SeasonSerializer(required=False)
    currentEvent = EventSerializer(required=False)
    userGroups = GroupSerializer(many=True)
    phoneTypes = PhoneTypeSerializer(many=True)
    fieldSchedule = ScoutFieldScheduleSerializer(many=True)
    # pitSchedule = ScoutPitScheduleSerializer(many=True)
    # pastSchedule = ScoutScheduleSerializer(many=True)
    scoutQuestionType = FormTypeSerializer(many=True)
    teams = TeamSerializer(many=True)


class ScoutColSerializer(serializers.Serializer):
    PropertyName = serializers.CharField()
    ColLabel = serializers.CharField()
    order = serializers.CharField()


class ScoutResultAnswerSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance


class ScoutFieldResultsSerializer(serializers.Serializer):
    scoutCols = ScoutColSerializer(many=True)
    scoutAnswers = ScoutResultAnswerSerializer(many=True)


class ScoutingUserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    under_review = serializers.BooleanField(required=False)


class UserActivitySerializer(serializers.Serializer):
    user = UserSerializer()
    user_info = ScoutingUserInfoSerializer()
    results = ScoutFieldResultsSerializer()
    schedule = ScoutFieldScheduleSerializer(many=True)

