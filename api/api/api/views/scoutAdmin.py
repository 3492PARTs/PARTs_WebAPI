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

        return seasons

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            req = self.get_init()
            serializer = SeasonSerializer(req, many=True)
            return Response(serializer.data)
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
                'date_st': e['start_date'],
                'date_end': e['end_date'],
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
            db.event_team_xref.delete().where((db.event_team_xref.team_no.not_in(e['teams_to_keep']) & (
                        db.event_team_xref.event == db.event.select(db.event.event_id).where(
                    db.event.event_cd == e['event_cd'])))).execute()

            try:
                db.event(event_nm=e['event_nm'], date_st=e['date_st'], date_end=e['date_end'],
                         event_cd=e['event_cd']).save(force_insert=True)
                messages += "Added event to DB: " + e['event_cd'] + '\n'
            except peewee.IntegrityError:
                messages += "Event already in DB: " + e['event_cd'] + '\n'

            for t in e['teams']:

                try:
                    db.team(team_no=t['team_no'], team_nm=t['team_nm']).save(force_insert=True)
                    messages += "Added team to DB: " + str(t['team_no']) + " " + t['team_nm'] + '\n'
                except peewee.IntegrityError:
                    messages += "Team already in DB: " + str(t['team_no']) + " " + t['team_nm'] + '\n'

                try:
                    db.event_team_xref(team_no=t['team_no'],
                                       event_id=(db.event.select(db.event.event_id).where(
                                           db.event.event_cd == e['event_cd']))).save(force_insert=True)
                    messages += "Added team to event in DB: " + str(t['team_no']) + " " + t['team_nm'] + " event: " + e[
                        'event_cd'] + '\n'
                except peewee.IntegrityError:
                    messages += "Team already in DB at event: " + str(t['team_no']) + " " + t['team_nm'] + " event: " + \
                                e['event_cd'] + '\n'

        return seasons

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            req = self.sync_season(request)
            serializer = SeasonSerializer(req, many=True)
            return Response(serializer.data)
        else:
            return ret_message('You do not have access', True)
