import datetime
import pytz
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json

import user.util
from form.models import QuestionAnswer, Question, QuestionOption, QuestionType, FormSubType, FormType
from general import send_message
from user.models import User, PhoneType

from .serializers import *
from scouting.models import Season, Event, ScoutAuthGroups, ScoutFieldSchedule, Team, \
    CompetitionLevel, Match, EventTeamInfo, ScoutField, ScoutPit
from rest_framework.views import APIView
from general.security import has_access, ret_message
import requests
from django.conf import settings
from django.db.models.functions import Lower
from django.db.models import Q
from rest_framework.response import Response
import form.util

auth_obj = 'scoutadmin'
app_url = 'scouting/admin/'


class Init(APIView):
    """
    API endpoint to get all the init values for the scout admin screen
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'init/'

    def init(self):
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

        user_groups = []
        try:
            user_groups = user.util.get_all_user_groups().filter(id__in=list(
                ScoutAuthGroups.objects.all().values_list('auth_group_id', flat=True)))
        except Exception as e:
            user_groups = []

        phone_types = user.util.get_phone_types()

        fieldSchedule = []

        fsf = ScoutFieldSchedule.objects.select_related('red_one', 'red_two', 'red_three', 'blue_one', 'blue_two',
                                                        'blue_three').filter(
            event=current_event, void_ind='n').order_by('notification3', 'st_time')

        for fs in fsf:
            fieldSchedule.append({
                'scout_field_sch_id': fs.scout_field_sch_id,
                'event_id': fs.event_id,
                'st_time': fs.st_time,
                'end_time': fs.end_time,
                'notification1': fs.notification1,
                'notification2': fs.notification2,
                'notification3': fs.notification3,
                'red_one_id': fs.red_one,
                'red_two_id': fs.red_two,
                'red_three_id': fs.red_three,
                'blue_one_id': fs.blue_one,
                'blue_two_id': fs.blue_two,
                'blue_three_id': fs.blue_three,
                'scouts': 'R1: ' +
                          ('' if fs.red_one is None else fs.red_one.first_name + ' ' + fs.red_one.last_name[0:1]) +
                          '\nR2: ' +
                          ('' if fs.red_two is None else fs.red_two.first_name + ' ' + fs.red_two.last_name[0:1]) +
                          '\nR3: ' +
                          ('' if fs.red_three is None else fs.red_three.first_name + ' ' + fs.red_three.last_name[
                                                                                           0:1]) +
                          '\nB1: ' +
                          ('' if fs.blue_one is None else fs.blue_one.first_name + ' ' + fs.blue_one.last_name[0:1]) +
                          '\nB2: ' +
                          ('' if fs.blue_two is None else fs.blue_two.first_name + ' ' + fs.blue_two.last_name[0:1]) +
                          '\nB3: ' +
                          ('' if fs.blue_three is None else fs.blue_three.first_name + ' ' + fs.blue_three.last_name[
                                                                                             0:1])
            })

        teams = Team.objects.filter(void_ind='n').order_by('team_no')

        scoutQuestionType = FormType.objects.all()

        return {'seasons': seasons, 'events': events, 'currentSeason': current_season, 'currentEvent': current_event,
                'userGroups': user_groups, 'phoneTypes': phone_types,
                'fieldSchedule': fieldSchedule,  # 'pitSchedule': pitSchedule,
                'scoutQuestionType': scoutQuestionType, 'teams': teams}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.init()
                serializer = InitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id,
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
                'webcast_url': e['webcasts'][0]['channel'] if len(e['webcasts']) > 0 else '',
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
                      event_cd=e['event_cd'], event_url=e['event_url'], address=e['address'], city=e['city'],
                      state_prov=e['state_prov'], postal_code=e['postal_code'], location_name=e['location_name'],
                      gmaps_url=e['gmaps_url'], webcast_url=e['webcast_url'], timezone=e['timezone'], current='n',
                      competition_page_active='n', void_ind='n').save(force_insert=True)
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
                return ret_message('An error occurred while syncing the season/event/teams.', True,
                                   app_url + self.endpoint,
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
        match_number = ""
        try:
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
                    match = Match(match_id=match_key, match_number=match_number, event=event, red_one=red_one,
                                  red_two=red_two, red_three=red_three, blue_one=blue_one,
                                  blue_two=blue_two, blue_three=blue_three, red_score=red_score, blue_score=blue_score,
                                  comp_level=comp_level, time=time, void_ind='n')
                    match.save()
                    messages += '(ADD) ' + event.event_nm + \
                                ' ' + comp_level.comp_lvl_typ_nm + \
                                ' ' + str(match_number) + ' ' + match_key + '\n'
        except:
            messages += '(EROR) ' + event.event_nm + \
                        ' ' + match_number + '\n'
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


class SyncEventTeamInfo(APIView):
    """
    API endpoint to sync the info for a teams at an event
    """
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = 'sync-event-team-info/'

    def sync_event_team_info(self):
        event = Event.objects.get(current='y')

        insert = []
        messages = ''
        r = requests.get("https://www.thebluealliance.com/api/v3/event/" +
                         event.event_cd + "/rankings", headers={"X-TBA-Auth-Key": settings.TBA_KEY})
        r = json.loads(r.text)

        if r is None:
            return 'Nothing to sync'

        for e in r.get('rankings', []):
            matches_played = e.get('matches_played', 0)
            qual_average = e.get('qual_average', 0)
            losses = e.get('record', 0).get('losses', 0)
            wins = e.get('record', 0).get('wins', 0)
            ties = e.get('record', 0).get('ties', 0)
            rank = e.get('rank', 0)
            dq = e.get('dq', 0)
            team = Team.objects.get(
                Q(team_no=e['team_key'].replace('frc', '')) & Q(void_ind='n'))

            try:
                eti = EventTeamInfo.objects.get(
                    Q(event=event) & Q(team_no=team) & Q(void_ind='n'))

                eti.matches_played = matches_played
                eti.qual_average = qual_average
                eti.losses = losses
                eti.wins = wins
                eti.ties = ties
                eti.rank = rank
                eti.dq = dq

                eti.save()
                messages += '(UPDATE) ' + event.event_nm + \
                            ' ' + str(team.team_no) + '\n'
            except ObjectDoesNotExist as odne:
                eti = EventTeamInfo(event=event, team_no=team, matches_played=matches_played, qual_average=qual_average,
                                    losses=losses, wins=wins, ties=ties, rank=rank, dq=dq)
                eti.save()
                messages += '(ADD) ' + event.event_nm + \
                            ' ' + str(team.team_no) + '\n'

        return messages

    def get(self, request, format=None):
        if True or has_access(request.user.id, auth_obj):
            try:
                req = self.sync_event_team_info()
                return ret_message(req)
            except Exception as e:
                return ret_message('An error occurred while syncing event team info.', True, app_url + self.endpoint,
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
            return ret_message('No active event, can\'t activate competition page', True, app_url + self.endpoint,
                               self.request.user.id, odne)

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
            scout_field_answers = QuestionAnswer.objects.filter(
                scout_field=sf)
            for sfa in scout_field_answers:
                sfa.delete()
            sf.delete()

        scout_pits = ScoutPit.objects.filter(event=e)
        for sp in scout_pits:
            scout_pit_answers = QuestionAnswer.objects.filter(scout_pit=sp)
            for spa in scout_pit_answers:
                spa.delete()
            sp.delete()

        matches = Match.objects.filter(event=e)
        for m in matches:
            m.delete()

        scout_field_schedules = ScoutFieldSchedule.objects.filter(event=e)
        for sfs in scout_field_schedules:
            sfs.delete()
        """
        scout_pit_schedules = ScoutPitSchedule.objects.filter(event=e)
        for sps in scout_pit_schedules:
            sps.delete()
        """
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
        serializer = TeamCreateSerializer(data=request.data)
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
        serializer = EventTeamSerializer(data=request.data)
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
                scout_field_answers = QuestionAnswer.objects.filter(
                    scout_field=sf)
                for sfa in scout_field_answers:
                    sfa.delete()
                sf.delete()

            scout_pits = ScoutPit.objects.filter(event=e)
            for sp in scout_pits:
                scout_pit_answers = QuestionAnswer.objects.filter(scout_pit=sp)
                for spa in scout_pit_answers:
                    spa.delete()
                sp.delete()

            scout_questions = Question.objects.filter(season=season)
            for sq in scout_questions:
                question_options = QuestionOption.objects.filter(question=sq)
                for qo in question_options:
                    qo.delete()
                sq.delete()

            matches = Match.objects.filter(event=e)
            for m in matches:
                m.delete()

            scout_field_schedules = ScoutFieldSchedule.objects.filter(event=e)
            for sfs in scout_field_schedules:
                sfs.delete()
            """
            scout_pit_schedules = ScoutPitSchedule.objects.filter(event=e)
            for sps in scout_pit_schedules:
                sps.delete()
            """
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
            sfs.red_one_id = serializer.validated_data.get('red_one_id', None)
            sfs.red_two_id = serializer.validated_data.get('red_two_id', None)
            sfs.red_three_id = serializer.validated_data.get('red_three_id', None)
            sfs.blue_one_id = serializer.validated_data.get('blue_one_id', None)
            sfs.blue_two_id = serializer.validated_data.get('blue_two_id', None)
            sfs.blue_three_id = serializer.validated_data.get('blue_three_id', None)
            sfs.st_time = serializer.validated_data['st_time']
            sfs.end_time = serializer.validated_data['end_time']
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
            send_message.send_email(
                sfs.red_one.phone + sfs.red_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.red_one.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                       (sfs.red_one.first_name if sfs.red_one is not None else "red one") + '\n'
        try:
            send_message.send_email(
                sfs.red_two.phone + sfs.red_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.red_two.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                       (sfs.red_two.first_name if sfs.red_two is not None else "red two") + '\n'
        try:
            send_message.send_email(
                sfs.red_three.phone + sfs.red_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.red_three.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                       (sfs.red_three.first_name if sfs.red_three is not None else "red three") + '\n'
        try:
            send_message.send_email(
                sfs.blue_one.phone + sfs.blue_one.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.blue_one.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                       (sfs.blue_one.first_name if sfs.blue_one is not None else "blue one") + '\n'
        try:
            send_message.send_email(
                sfs.blue_two.phone + sfs.blue_two.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.blue_two.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                       (sfs.blue_two.first_name if sfs.blue_two is not None else "blue two") + '\n'
        try:
            send_message.send_email(
                sfs.blue_three.phone + sfs.blue_three.phone_type.phone_type, 'Time to Scout!', 'notify_scout', data)
            message += 'Notified: ' + sfs.blue_three.first_name + '\n'
        except Exception as e:
            message += 'Unable to notify: ' + \
                       (sfs.blue_three.first_name if sfs.blue_three is not None else "blue three") + '\n'

        discord_message = f'Scheduled time for scouting from ' \
                          f'{date_st_str} to {date_end_str} : '

        discord_message += ((f'<@{sfs.red_one.discord_user_id}>' if sfs.red_one.discord_user_id is not None
                             else sfs.red_one.first_name) if sfs.red_one is not None else "red one") + ', '

        discord_message += ((f'<@{sfs.red_two.discord_user_id}>' if sfs.red_two.discord_user_id is not None
                             else sfs.red_two.first_name) if sfs.red_two is not None else "red two") + ', '

        discord_message += ((f'<@{sfs.red_three.discord_user_id}>' if sfs.red_three.discord_user_id is not None
                             else sfs.red_three.first_name) if sfs.red_three is not None else "red three") + ', '

        discord_message += ((f'<@{sfs.blue_one.discord_user_id}>' if sfs.blue_one.discord_user_id is not None
                             else sfs.blue_one.first_name) if sfs.blue_one is not None else "blue one") + ', '

        discord_message += ((f'<@{sfs.blue_two.discord_user_id}>' if sfs.blue_two.discord_user_id is not None
                             else sfs.blue_two.first_name) if sfs.blue_two is not None else "blue two") + ', '

        discord_message += ((f'<@{sfs.blue_three.discord_user_id}>' if sfs.blue_three.discord_user_id is not None
                             else sfs.blue_three.first_name) if sfs.blue_three is not None else "blue three")

        send_message.send_discord_notification(discord_message)

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
