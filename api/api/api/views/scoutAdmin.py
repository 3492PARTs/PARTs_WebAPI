from datetime import datetime

import pytz
from django.db import IntegrityError
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json

from api.api.serializers import *
from api.api.models import *
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from api.auth.security import *
import requests


class GetScoutAdminInit(APIView):
    """
    API endpoint to get all the init values for the scout admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self):
        seasons = Season.objects.all()
        current_season = Season.objects.get(current='y')
        events = Event.objects.filter(void_ind='n')
        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            current_event = Event()

        return {'seasons': seasons, 'events': events, 'currentSeason': current_season, 'currentEvent': current_event}

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.get_init()
                serializer = ScoutAdminInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutAdminSyncSeason(APIView):
    """
    API endpoint to sync a season
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def sync_season(self, season_id):
        season = Season.objects.get(season_id=season_id)

        insert = []

        r = requests.get("https://www.thebluealliance.com/api/v3/team/frc3492/events/" + str(season.season),
                         headers={"X-TBA-Auth-Key": "vOi134WDqMjUjGslV08r9ElOGoiWAU8LtSMxMBPziTVertNPmsdUqBOY8cYnyb7u"})
        r = json.loads(r.text)

        for e in r:
            event_ = {
                'event_nm': e['name'],
                'date_st': datetime.strptime(e['start_date'], '%Y-%m-%d').astimezone(pytz.utc),
                'date_end': datetime.strptime(e['end_date'], '%Y-%m-%d').astimezone(pytz.utc),
                'event_cd': e['key'],
                'teams': [],
                'teams_to_keep': []
            }

            s = requests.get("https://www.thebluealliance.com/api/v3/event/" + e['key'] + "/teams",
                             headers={
                                 "X-TBA-Auth-Key": "vOi134WDqMjUjGslV08r9ElOGoiWAU8LtSMxMBPziTVertNPmsdUqBOY8cYnyb7u"})
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
            # remove teams that have been removed from an event
            EventTeamXref.objects.filter(~Q(team_no__in=e['teams_to_keep']) &
                                         Q(event=Event.objects.get(event_cd=e['event_cd']).event_id)).delete()

            try:
                Event(season=season, event_nm=e['event_nm'], date_st=e['date_st'], date_end=e['date_end'],
                      event_cd=e['event_cd']).save()
                messages += "(ADD) Added event: " + e['event_cd'] + '\n'
            except IntegrityError:
                messages += "(NO ADD) Already have event: " + e['event_cd'] + '\n'

            for t in e['teams']:

                try:
                    Team(team_no=t['team_no'], team_nm=t['team_nm']).save(force_insert=True)
                    messages += "(ADD) Added team: " + str(t['team_no']) + " " + t['team_nm'] + '\n'
                except IntegrityError:
                    messages += "(NO ADD) Already have team: " + str(t['team_no']) + " " + t['team_nm'] + '\n'

                try:
                    EventTeamXref(team_no=Team.objects.get(team_no=t['team_no']),
                                  event=Event.objects.get(event_cd=e['event_cd'])).save()
                    messages += "(ADD) Added team: " + str(t['team_no']) + " " + t['team_nm'] + " to event: " + e[
                        'event_cd'] + '\n'
                except IntegrityError:
                    messages += "(NO ADD) Team: " + str(t['team_no']) + " " + t['team_nm'] + " already at event: " + \
                                e['event_cd'] + '\n'

        return messages

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.sync_season(request.query_params.get('season_id', None))
                return ret_message(req)
            except Exception as e:
                return ret_message('An error occurred while syncing teams', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutAdminSetSeason(APIView):
    """
    API endpoint to set the season
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def set(self, season_id, event_id):
        msg = ""

        Season.objects.filter(current='y').update(current='n')
        season = Season.objects.get(season_id=season_id)
        season.current = 'y'
        season.save()
        msg = "Successfully set the season to: " + season.season

        if event_id is not None:
            Event.objects.filter(current='y').update(current='n')
            event = Event.objects.get(event_id=event_id)
            event.current = 'y'
            event.save()
            msg += "\nSuccessfully set the event to: " + event.event_nm

        return ret_message(msg)

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.set(request.query_params.get('season_id', None), request.query_params.get('event_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while setting the season', True, e)
        else:
            return ret_message('You do not have access', True)