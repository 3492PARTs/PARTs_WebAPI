import datetime
import pytz
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json
from user.models import User

from .serializers import Event3Serializer, EventSerializer, EventToTeamsSerializer, InitSerializer, ScoutAdminQuestionInitSerializer, ScoutFieldScheduleSaveSerializer, ScoutQuestionSerializer, Team3Serializer
from user.serializers import PhoneTypeSerializer, Group, PhoneType
from scouting.models import Season, Event, ScoutAuthGroups, ScoutFieldSchedule, ScoutPitSchedule, ScoutQuestionType, Team, CompetitionLevel, Match, ScoutField, ScoutFieldAnswer, ScoutPit, ScoutPitAnswer, ScoutQuestion, ScoutQuestionSubType, QuestionOptions, QuestionType
from general import send_email
from rest_framework.views import APIView
from general.security import has_access, ret_message
import requests
from django.conf import settings
from django.db.models.functions import Lower
from django.db.models import Q
from rest_framework.response import Response


auth_obj = 50
app_url = 'scouting/admin/'


class Init(APIView):
    """
    API endpoint to get all the init values for the scout admin screen
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'init/'

    def get_init(self):
        seasons = Season.objects.all().order_by('season')
        events = Event.objects.filter(void_ind='n').order_by(
            'season__season', Lower('event_nm'))

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            current_season = Season()

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            current_event = Event()

        users = User.objects.filter(Q(is_active=True) & Q(
            date_joined__isnull=False) & ~Q(groups__name__in=['Admin'])).order_by(Lower('first_name'), Lower('last_name'))

        user_groups = []
        try:
            user_groups = Group.objects.filter(id__in=list(
                ScoutAuthGroups.objects.all().values_list('auth_group_id', flat=True))).order_by('name')
        except Exception as e:
            user_groups = []

        phone_types = PhoneType.objects.all().order_by(Lower('carrier'))

        fieldSchedule = []

        fieldSchedule = ScoutFieldSchedule.objects.select_related('red_one', 'red_two', 'red_three', 'blue_one', 'blue_two', 'blue_three').filter(
            event=current_event, void_ind='n').order_by('-st_time')

        pitSchedule = ScoutPitSchedule.objects.filter(
            event=current_event, void_ind='n').order_by('-st_time')

        teams = Team.objects.filter(void_ind='n').order_by('team_no')

        """
        pastSchedule = []
        sss = ScoutSchedule.objects.filter(Q(end_time__lt=time) & Q(
            void_ind='n')).order_by('st_time', 'user')
        for ss in sss:
            pastSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'st_time': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified,
                'void_ind': ss.void_ind,
                'st_time_str': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time_str': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
            })
        """
        scoutQuestionType = ScoutQuestionType.objects.all()

        return {'seasons': seasons, 'events': events, 'currentSeason': current_season, 'currentEvent': current_event,
                'users': users, 'userGroups': user_groups, 'phoneTypes': phone_types,
                'fieldSchedule': fieldSchedule, 'pitSchedule': pitSchedule,
                'scoutQuestionType': scoutQuestionType, 'teams': teams}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init()
                serializer = InitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint, request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SyncSeason(APIView):
    """
    API endpoint to sync a season
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'sync-season/'

    def sync_season(self, season_id):
        season = Season.objects.get(season_id=season_id)

        insert = []

        r = requests.get("https://www.thebluealliance.com/api/v3/team/frc3492/events/" + str(season.season),
                         headers={"X-TBA-Auth-Key": settings.TBA_KEY})
        r = json.loads(r.text)

        for e in r:
            time_zone = e.get('timezone') if e.get(
                'timezone', None) is not None else 'America/New_York'
            event_ = {
                'event_nm': e['name'],
                'date_st': datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').astimezone(pytz.timezone(time_zone)),
                'date_end': datetime.datetime.strptime(e['end_date'], '%Y-%m-%d').astimezone(pytz.timezone(time_zone)),
                'event_cd': e['key'],
                'event_url': e.get('event_url', None),
                'gmaps_url': e.get('gmaps_url', None),
                'address': e.get('address', None),
                'city': e.get('city', None),
                'state_prov': e.get('state_prov', None),
                'postal_code': e.get('postal_code', None),
                'location_name': e.get('location_name', None),
                'timezone': e.get('timezone', 'America/New_York'),
                'webcast_url':  e['webcasts'][0]['channel'] if len(e['webcasts']) > 0 else '',
                'teams': [],
                'teams_to_keep': []
            }

            s = requests.get("https://www.thebluealliance.com/api/v3/event/" + e['key'] + "/teams",
                             headers={
                                 "X-TBA-Auth-Key": settings.TBA_KEY})
            s = json.loads(s.text)

            for t in s:
                event_['teams'].append({
                    'team_no': t['team_number'],
                    'team_nm': t['nickname']
                })

                event_['teams_to_keep'].append(t['team_number'])

            insert.append(event_)

        messages = ''
        for e in insert:

            try:
                Event(season=season, event_nm=e['event_nm'], date_st=e['date_st'], date_end=e['date_end'],
                      event_cd=e['event_cd'], event_url=e['event_url'], address=e['address'], city=e['city'], state_prov=e['state_prov'], postal_code=e['postal_code'], location_name=e['location_name'], gmaps_url=e['gmaps_url'], webcast_url=e['webcast_url'], timezone=e['timezone'], current='n', competition_page_active='n', void_ind='n').save(force_insert=True)
                messages += "(ADD) Added event: " + e['event_cd'] + '\n'
            except IntegrityError:
                event = Event.objects.get(
                    Q(event_cd=e['event_cd']) & Q(void_ind='n'))
                event.date_st = e['date_st']
                event.event_url = e['event_url']
                event.address = e['address']
                event.city = e['city']
                event.state_prov = e['state_prov']
                event.postal_code = e['postal_code']
                event.location_name = e['location_name']
                event.gmaps_url = e['gmaps_url']
                event.webcast_url = e['webcast_url']
                event.date_end = e['date_end']
                event.timezone = e['timezone']
                event.save()

                messages += "(NO ADD) Already have event: " + \
                    e['event_cd'] + '\n'

            # remove teams that have been removed from an event
            event = Event.objects.get(event_cd=e['event_cd'], void_ind='n')
            teams = Team.objects.filter(
                ~Q(team_no__in=e['teams_to_keep']) & Q(event=event))
            for team in teams:
                team.event_set.remove(event)

            for t in e['teams']:

                try:
                    Team(team_no=t['team_no'], team_nm=t['team_nm'], void_ind='n').save(
                        force_insert=True)
                    messages += "(ADD) Added team: " + \
                        str(t['team_no']) + " " + t['team_nm'] + '\n'
                except IntegrityError:
                    messages += "(NO ADD) Already have team: " + \
                        str(t['team_no']) + " " + t['team_nm'] + '\n'

                try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
                    team = Team.objects.get(team_no=t['team_no'])
                    team.event_set.add(
                        Event.objects.get(event_cd=e['event_cd'], void_ind='n'))
                    messages += "(ADD) Added team: " + str(t['team_no']) + " " + t['team_nm'] + " to event: " + e[
                        'event_cd'] + '\n'
                except IntegrityError:
                    messages += "(NO ADD) Team: " + str(t['team_no']) + " " + t['team_nm'] + " already at event: " + \
                                e['event_cd'] + '\n'

        return messages

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.sync_season(
                    request.query_params.get('season_id', None))
                return ret_message(req)
            except Exception as e:
                return ret_message('An error occurred while syncing the season/event/teams.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SyncMatches(APIView):
    """
    API endpoint to sync a season
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'sync-matches/'

    def sync_matches(self):
        event = Event.objects.get(current='y')

        insert = []
        messages = ''
        r = requests.get("https://www.thebluealliance.com/api/v3/event/" +
                         event.event_cd + "/matches", headers={"X-TBA-Auth-Key": settings.TBA_KEY})
        r = json.loads(r.text)

        for e in r:
            match_number = e.get('match_number', 0)
            red_one = Team.objects.get(
                Q(team_no=e['alliances']['red']['team_keys'][0].replace('frc', '')) & Q(void_ind='n'))
            red_two = Team.objects.get(
                Q(team_no=e['alliances']['red']['team_keys'][1].replace('frc', '')) & Q(void_ind='n'))
            red_three = Team.objects.get(
                Q(team_no=e['alliances']['red']['team_keys'][2].replace('frc', '')) & Q(void_ind='n'))
            blue_one = Team.objects.get(
                Q(team_no=e['alliances']['blue']['team_keys'][0].replace('frc', '')) & Q(void_ind='n'))
            blue_two = Team.objects.get(
                Q(team_no=e['alliances']['blue']['team_keys'][1].replace('frc', '')) & Q(void_ind='n'))
            blue_three = Team.objects.get(
                Q(team_no=e['alliances']['blue']['team_keys'][2].replace('frc', '')) & Q(void_ind='n'))
            red_score = e['alliances']['red'].get('score', None)
            blue_score = e['alliances']['blue'].get('score', None)
            comp_level = CompetitionLevel.objects.get(Q(
                comp_lvl_typ=e.get('comp_level', ' ')) & Q(void_ind='n'))
            time = datetime.datetime.fromtimestamp(
                e['time'], pytz.timezone('America/New_York')) if e['time'] else None
            match_key = e['key']

            try:
                if (comp_level.comp_lvl_typ == 'qf'):
                    print(e)
                match = Match.objects.get(
                    Q(match_id=match_key) & Q(void_ind='n'))

                match.red_one = red_one
                match.red_two = red_two
                match.red_three = red_three
                match.blue_one = blue_one
                match.blue_two = blue_two
                match.blue_three = blue_three
                match.red_score = red_score
                match.blue_score = blue_score
                match.comp_level = comp_level
                match.time = time

                match.save()
                messages += '(UPDATE) ' + event.event_nm + \
                    ' ' + comp_level.comp_lvl_typ_nm + \
                    ' ' + str(match_number) + ' ' + match_key + '\n'
            except ObjectDoesNotExist as odne:
                match = Match(match_id=match_key, match_number=match_number, event=event, red_one=red_one, red_two=red_two, red_three=red_three, blue_one=blue_one,
                              blue_two=blue_two, blue_three=blue_three, red_score=red_score, blue_score=blue_score, comp_level=comp_level, time=time, void_ind='n')
                match.save()
                messages += '(ADD) ' + event.event_nm + \
                    ' ' + comp_level.comp_lvl_typ_nm + \
                    ' ' + str(match_number) + ' ' + match_key + '\n'

        return messages

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.sync_matches()
                return ret_message(req)
            except Exception as e:
                return ret_message('An error occurred while syncing matches.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SetSeason(APIView):
    """
    API endpoint to set the season
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'set-season/'

    def set(self, season_id, event_id):
        msg = ""

        Season.objects.filter(current='y').update(current='n')
        season = Season.objects.get(season_id=season_id)
        season.current = 'y'
        season.save()
        msg = "Successfully set the season to: " + season.season

        if event_id is not None:
            Event.objects.filter(current='y').update(
                current='n', competition_page_active='n')
            event = Event.objects.get(event_id=event_id)
            event.current = 'y'
            event.save()
            msg += "\nSuccessfully set the event to: " + event.event_nm

        return ret_message(msg)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.set(request.query_params.get(
                    'season_id', None), request.query_params.get('event_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while setting the season.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class ToggleCompetitionPage(APIView):
    """
    API endpoint to toggle a scout field question
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'toggle-competition-page/'

    def toggle(self, sq_id):
        try:
            event = Event.objects.get(Q(current='y') & Q(void_ind='n'))

            if event.competition_page_active == 'n':
                event.competition_page_active = 'y'
            else:
                event.competition_page_active = 'n'
            event.save()
        except ObjectDoesNotExist as odne:
            return ret_message('No active event, can\'t activate competition page', True, app_url + self.endpoint, self.request.user.id, odne)

        return ret_message('Successfully  activated competition page.')

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.toggle(request.query_params.get('sq_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the competition page.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class AddSeason(APIView):
    """
    API endpoint to add a season
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'add-season/'

    def add(self, season):
        try:
            Season.objects.get(season=season)
            return ret_message('Season not added. Season ' + season + ' already exists.', True,
                               app_url + self.endpoint, self.request.user.id)
        except Exception as e:
            Season(season=season, current='n').save()

        return ret_message('Successfully added season: ' + season)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.add(request.query_params.get('season', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while setting the season.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class AddEvent(APIView):
    """
    API endpoint to add a event
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'add-event/'

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                serializer.save()
                return ret_message('Successfully added the event.')
            except Exception as e:
                return ret_message('An error occurred while saving the event.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class DeleteEvent(APIView):
    """
    API endpoint to delete an event
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'delete-event/'

    def delete(self, event_id):
        e = Event.objects.get(event_id=event_id)

        teams_at_event = Team.objects.filter(event=e)
        for t in teams_at_event:
            t.event_set.remove(e)

        scout_fields = ScoutField.objects.filter(event=e)
        for sf in scout_fields:
            scout_field_answers = ScoutFieldAnswer.objects.filter(
                scout_field=sf)
            for sfa in scout_field_answers:
                sfa.delete()
            sf.delete()

        scout_pits = ScoutPit.objects.filter(event=e)
        for sp in scout_pits:
            scout_pit_answers = ScoutPitAnswer.objects.filter(scout_pit=sp)
            for spa in scout_pit_answers:
                spa.delete()
            sp.delete()

        matches = Match.objects.filter(event=e)
        for m in matches:
            m.delete()

        scout_field_schedules = ScoutFieldSchedule.objects.filter(event=e)
        for sfs in scout_field_schedules:
            sfs.delete()

        scout_pit_schedules = ScoutPitSchedule.objects.filter(event=e)
        for sps in scout_pit_schedules:
            sps.delete()

        e.delete()

        return ret_message('Successfully deleted event: ' + e.event_nm)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.delete(request.query_params.get('event_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while deleting the event.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class AddTeam(APIView):
    """
    API endpoint to add a event
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'add-team/'

    def post(self, request, format=None):
        serializer = Team3Serializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                serializer.save()
                return ret_message('Successfully added the team.')
            except Exception as e:
                return ret_message('An error occurred while saving the team.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class AddTeamToEvent(APIView):
    """
    API endpoint to add a team to an event
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'add-team-to-event/'

    def link(self, data):
        messages = ''

        for t in data.get('teams', []):
            try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
                if t.get('checked', False):
                    team = Team.objects.get(team_no=t['team_no'], void_ind='n')
                    e = Event.objects.get(
                        event_id=data['event_id'], void_ind='n')
                    team.event_set.add(e)
                    messages += "(ADD) Added team: " + str(
                        t['team_no']) + " " + t['team_nm'] + " to event: " + e.event_cd + '\n'
            except IntegrityError:
                messages += "(NO ADD) Team: " + str(t['team_no']) + " " + t['team_nm'] + " already at event: " + \
                            e.event_cd + '\n'

        return messages

    def post(self, request, format=None):
        serializer = EventToTeamsSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.link(serializer.validated_data)
                return ret_message(req)
            except Exception as e:
                return ret_message('An error occurred while saving the team.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class RemoveTeamToEvent(APIView):
    """
    API endpoint to remove a team from an event
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'remove-team-to-event/'

    def link(self, data):
        messages = ''

        for t in data.get('team_no', []):
            try:  # TODO it doesn't throw an error, but re-linking many to many only keeps one entry in the table for the link
                if not t.get('checked', True):
                    team = Team.objects.get(team_no=t['team_no'], void_ind='n')
                    e = Event.objects.get(
                        event_id=data['event_id'], void_ind='n')
                    team.event_set.remove(e)
                    messages += "(REMOVE) Removed team: " + str(
                        t['team_no']) + " " + t['team_nm'] + " from event: " + e.event_cd + '\n'
            except IntegrityError:
                messages += "(NO REMOVE) Team: " + str(t['team_no']) + " " + t['team_nm'] + " from event: " + \
                            e.event_cd + '\n'

        return messages

    def post(self, request, format=None):
        serializer = Event3Serializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.link(serializer.validated_data)
                return ret_message(req)
            except Exception as e:
                return ret_message('An error occurred while removing the team.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class DeleteSeason(APIView):
    """
    API endpoint to delete a season
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'delete-season/'

    def delete(self, season_id):
        season = Season.objects.get(season_id=season_id)

        events = Event.objects.filter(season=season)
        for e in events:
            teams_at_event = Team.objects.filter(event=e)
            for t in teams_at_event:
                t.event_set.remove(e)

            scout_fields = ScoutField.objects.filter(event=e)
            for sf in scout_fields:
                scout_field_answers = ScoutFieldAnswer.objects.filter(
                    scout_field=sf)
                for sfa in scout_field_answers:
                    sfa.delete()
                sf.delete()

            scout_pits = ScoutPit.objects.filter(event=e)
            for sp in scout_pits:
                scout_pit_answers = ScoutPitAnswer.objects.filter(scout_pit=sp)
                for spa in scout_pit_answers:
                    spa.delete()
                sp.delete()

            scout_questions = ScoutQuestion.objects.filter(season=season)
            for sq in scout_questions:
                question_options = QuestionOptions.objects.filter(sq=sq)
                for qo in question_options:
                    qo.delete()
                sq.delete()

            matches = Match.objects.filter(event=e)
            for m in matches:
                m.delete()

            scout_field_schedules = ScoutFieldSchedule.objects.filter(event=e)
            for sfs in scout_field_schedules:
                sfs.delete()

            scout_pit_schedules = ScoutPitSchedule.objects.filter(event=e)
            for sps in scout_pit_schedules:
                sps.delete()

            e.delete()

        season.delete()

        return ret_message('Successfully deleted season: ' + season.season)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.delete(request.query_params.get('season_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while deleting the season.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class QuestionInit(APIView):
    """
    API endpoint to get the question init values for the scout admin screen
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'question-init/'

    def get_init(self, question_type):
        question_types = QuestionType.objects.filter(void_ind='n')

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        scout_question_sub_types = ScoutQuestionSubType.objects.filter(
            sq_typ_id=question_type).order_by('sq_sub_nm')

        scout_questions = []
        try:
            scout_questions = ScoutQuestion.objects.prefetch_related('questionoptions_set').filter(
                Q(season=current_season) & Q(sq_typ_id=question_type)).order_by('sq_sub_typ_id', 'order')
            '''
            for sq in scout_questions:
                ops = QuestionOptions.objects.filter(sq=sq)
                options = []
                for op in ops:
                    options.append({
                        'q_opt_id': op.q_opt_id,
                        'option': op.option,
                        'sq': op.sq_id,
                        'active': op.active,
                        'void_ind': op.void_ind
                    })
                
                scout_questions.append({
                    'sq_id': sq.sq_id,
                    'season': sq.season_id,
                    'sq_typ': sq.sq_typ_id,
                    'sq_sub_typ': sq.sq_sub_typ_id,
                    'question_typ': sq.question_typ_id,
                    'question': sq.question,
                    'order': sq.order,
                    'active': sq.active,
                    'void_ind': sq.void_ind,
                    'options': options
                })
                '''
        except Exception as e:
            scout_questions = []

        return {'questionTypes': question_types, 'scoutQuestions': scout_questions, 'scoutQuestionSubTypes': scout_question_sub_types}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init(request.query_params.get('sq_typ', None))
                if type(req) == Response:
                    return req
                serializer = ScoutAdminQuestionInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'api/scoutAdmin/GetQuestionInit',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'api/scoutAdmin/GetQuestionInit', request.user.id)


class SaveScoutQuestion(APIView):
    """API endpoint to save new questions"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-scout-question/'

    def save_question(self, data):
        try:
            try:
                current_season = Season.objects.get(current='y')
            except Exception as e:
                return ret_message('No season set, see an admin.', True, app_url + self.endpoint,
                                   self.request.user.id, e)

            sq = ScoutQuestion(season=current_season, question_typ=data['question_typ'],  sq_typ=data['sq_typ'],
                               sq_sub_typ=data.get('sq_sub_typ', None),
                               question=data['question'], order=data['order'], active='y', void_ind='n')

            sq.save()

            # If adding a new question we need to make a null answer for it for all questions already answered
            if data['sq_typ'] == 'pit':
                questions_answered = ScoutPit.objects.filter(void_ind='n')

                for qa in questions_answered:
                    ScoutPitAnswer(scout_pit=qa, sq=sq,
                                   answer='!EXIST', void_ind='n').save()
            else:
                questions_answered = ScoutField.objects.filter(void_ind='n')

                for qa in questions_answered:
                    ScoutFieldAnswer(scout_field=qa, sq=sq,
                                     answer='!EXIST', void_ind='n').save()

            if data['sq_typ'] == 'select' and len(data.get('questionoptions_set', [])) <= 0:
                raise Exception('Select questions must have options.')

            for op in data.get('questionoptions_set', []):
                QuestionOptions(
                    option=op['option'], sq_id=sq.sq_id, active='y', void_ind='n').save()

            return ret_message('Saved question successfully.')
        except Exception as e:
            return ret_message('Couldn\'t save question', True, app_url + self.endpoint, self.request.user.id, e)

    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_question(serializer.validated_data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the question.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class UpdateScoutQuestion(APIView):
    """API endpoint to update questions"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'update-scout-question/'

    def update_question(self, data):
        sq = ScoutQuestion.objects.get(sq_id=data['sq_id'])

        sq.question = data['question']
        sq.order = data['order']
        sq.sq_sub_typ_id = data.get('sq_sub_typ', None)
        sq.question_typ_id = data['question_typ']
        sq.save()

        if data['sq_typ'] == 'select' and len(data.get('questionoptions_set', [])) <= 0:
            raise Exception('Select questions must have options.')

        for op in data.get('questionoptions_set', []):
            if op.get('q_opt_id', None) is not None:
                o = QuestionOptions.objects.get(q_opt_id=op['q_opt_id'])
                o.option = op['option']
                o.active = op['active']
                o.save()
            else:
                QuestionOptions(
                    option=op['option'], sq_id=sq.sq_id, active='y', void_ind='n').save()

        return ret_message('Question saved successfully')

    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.update_question(serializer.validated_data)
                return req
            except Exception as e:
                return ret_message('An error occurred while updating the question.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class ToggleScoutQuestion(APIView):
    """
    API endpoint to toggle a scout field question
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'toggle-scout-question/'

    def toggle(self, sq_id):
        sq = ScoutQuestion.objects.get(sq_id=sq_id)

        if sq.active == 'n':
            sq.active = 'y'
        else:
            sq.active = 'n'

        sq.save()

        return ret_message('Successfully toggled the question state.')

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.toggle(request.query_params.get('sq_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the scout question.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class ToggleOption(APIView):
    """
    API endpoint to toggle a question option
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'toggle-option/'

    def toggle(self, q_opt_id):
        opt = QuestionOptions.objects.get(q_opt_id=q_opt_id)

        if opt.active == 'n':
            opt.active = 'y'
        else:
            opt.active = 'n'

        opt.save()

        return ret_message('Successfully toggled the option.')

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.toggle(request.query_params.get('q_opt_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the option.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SaveScoutFieldScheduleEntry(APIView):
    """API endpoint to save scout schedule entry"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-scout-field-schedule-entry/'

    def save_scout_schedule(self, serializer):
        """
        if serializer.validated_data['st_time'] <= timezone.now():
            return ret_message('Start time can\'t be in the past.', True, app_url + self.endpoint,
                               self.request.user.id)
        """

        if serializer.validated_data['end_time'] <= serializer.validated_data['st_time']:
            return ret_message('End time can\'t come before start.', True, app_url + self.endpoint,
                               self.request.user.id)

        if serializer.validated_data.get('scout_field_sch_id', None) is None:
            serializer.save()
            return ret_message('Saved schedule entry successfully')
        else:
            sfs = ScoutFieldSchedule.objects.get(
                scout_field_sch_id=serializer.validated_data['scout_field_sch_id'])
            sfs.red_one = serializer.validated_data.get('red_one', None)
            sfs.red_two = serializer.validated_data.get('red_two', None)
            sfs.red_three = serializer.validated_data.get('red_three', None)
            sfs.blue_one = serializer.validated_data.get('blue_one', None)
            sfs.blue_two = serializer.validated_data.get('blue_two', None)
            sfs.blue_three = serializer.validated_data.get('blue_three', None)
            sfs.st_time = serializer.validated_data['st_time']
            sfs.end_time = serializer.validated_data['end_time']
            sfs.notified = 'n'
            sfs.void_ind = serializer.validated_data['void_ind']
            sfs.save()
            return ret_message('Updated schedule entry successfully')

    def post(self, request, format=None):
        serializer = ScoutFieldScheduleSaveSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_scout_schedule(serializer)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the schedule entry.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class NotifyUsers(APIView):
    """API endpoint to notify users"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'notify-users/'

    def notify_users(self, id):
        event = Event.objects.get(Q(current='y') & Q(void_ind='n'))
        sfs = ScoutFieldSchedule.objects.get(scout_field_sch_id=id)
        date_st_utc = sfs.st_time.astimezone(pytz.utc)
        date_end_utc = sfs.end_time.astimezone(pytz.utc)
        date_st_local = date_st_utc.astimezone(pytz.timezone(event.timezone))
        date_end_local = date_end_utc.astimezone(pytz.timezone(event.timezone))
        date_st_str = date_st_local.strftime("%m/%d/%Y, %I:%M%p")
        date_end_str = date_end_local.strftime("%m/%d/%Y, %I:%M%p")
        data = {
            'scout_location': 'Field',
            'scout_time_st': date_st_str,
            'scout_time_end': date_end_str,
            'lead_scout': self.request.user.first_name + ' ' + self.request.user.last_name
        }
        message = ''
        try:
            send_email.send_message(
                sfs.red_one.profile.phone + sfs.red_one.profile.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.red_one.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                (sfs.red_one.first_name if sfs.red_one is not None else "red one") + '\n'
        try:
            send_email.send_message(
                sfs.red_two.profile.phone + sfs.red_two.profile.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.red_two.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                (sfs.red_two.first_name if sfs.red_two is not None else "red two") + '\n'
        try:
            send_email.send_message(
                sfs.red_three.profile.phone + sfs.red_three.profile.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.red_three.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                (sfs.red_three.first_name if sfs.red_three is not None else "red three") + '\n'
        try:
            send_email.send_message(
                sfs.blue_one.profile.phone + sfs.blue_one.profile.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.blue_one.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                (sfs.blue_one.first_name if sfs.blue_one is not None else "blue one") + '\n'
        try:
            send_email.send_message(
                sfs.blue_two.profile.phone + sfs.blue_two.profile.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.blue_two.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                (sfs.blue_two.first_name if sfs.blue_two is not None else "blue two") + '\n'
        try:
            send_email.send_message(
                sfs.blue_three.profile.phone + sfs.blue_three.profile.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.blue_three.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                (sfs.blue_three.first_name if sfs.blue_three is not None else "blue three") + '\n'

        sfs.notified = 'y'
        sfs.save()

        return ret_message(message)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.notify_users(request.query_params.get(
                    'id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while notifying the users.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SavePhoneType(APIView):
    """API endpoint to save phone types"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-phone-type/'

    def save_phone_type(self, data):

        if data.get('phone_type_id', None) is not None:
            pt = PhoneType.objects.get(phone_type_id=data['phone_type_id'])
            pt.phone_type = data['phone_type']
            pt.carrier = data['carrier']
            pt.save()
        else:
            PhoneType(phone_type=data['phone_type'],
                      carrier=data['carrier']).save()

        return ret_message('Successfully saved phone type.')

    def post(self, request, format=None):
        serializer = PhoneTypeSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_phone_type(serializer.validated_data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving phone type.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)
