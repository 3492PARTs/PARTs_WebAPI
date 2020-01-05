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
from api.auth.models import AuthUser
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
        events = Event.objects.filter(void_ind='n')

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            current_season = Season()

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            current_event = Event()

        users = AuthUser.objects.all()

        return {'seasons': seasons, 'events': events, 'currentSeason': current_season, 'currentEvent': current_event,
                'users': users}

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

            try:
                Event(season=season, event_nm=e['event_nm'], date_st=e['date_st'], date_end=e['date_end'],
                      event_cd=e['event_cd'], current='n', void_ind='n').save(force_insert=True)
                messages += "(ADD) Added event: " + e['event_cd'] + '\n'
            except IntegrityError:
                messages += "(NO ADD) Already have event: " + e['event_cd'] + '\n'

            # remove teams that have been removed from an event
            EventTeamXref.objects.filter(~Q(team_no__in=e['teams_to_keep']) &
                                         Q(event=Event.objects.get(event_cd=e['event_cd']).event_id)).delete()

            for t in e['teams']:

                try:
                    Team(team_no=t['team_no'], team_nm=t['team_nm']).save(force_insert=True)
                    messages += "(ADD) Added team: " + str(t['team_no']) + " " + t['team_nm'] + '\n'
                except IntegrityError:
                    messages += "(NO ADD) Already have team: " + str(t['team_no']) + " " + t['team_nm'] + '\n'

                try:
                    EventTeamXref(team_no=Team.objects.get(team_no=t['team_no']),
                                  event=Event.objects.get(event_cd=e['event_cd'])).save(force_insert=True)
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


class GetScoutAdminAddSeason(APIView):
    """
    API endpoint to add a season
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def add(self, season):
        Season(season=season, current='n').save()

        return ret_message('Successfully added season: ' + season)

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.add(request.query_params.get('season', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while setting the season', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutAdminDeleteSeason(APIView):
    """
    API endpoint to delete a season
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, season_id):
        season = Season.objects.get(season_id=season_id)

        events = Event.objects.filter(season=season)

        for e in events:
            EventTeamXref.objects.filter(event=e).delete()

            scout_fields = ScoutField.objects.filter(event=e)

            for sf in scout_fields:
                ScoutFieldAnswer.objects.filter(scout_field=sf).delete()
                sf.delete()

            scout_pits = ScoutPit.objects.filter(event=e)

            for sp in scout_pits:
                ScoutPitAnswer.objects.filter(scout_pit=sp).delete()
                sp.delete()

            ScoutQuestion.objects.filter(season=season).delete()

            e.delete()

        season.delete()

        return ret_message('Successfully deleted season: ' + season.season)

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.delete(request.query_params.get('season_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while setting the season', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutAdminQuestionInit(APIView):
    """
    API endpoint to get all the init values for the scout admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self, question_type):
        question_types = QuestionType.objects.filter(void_ind='n')

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while initializing', True, e) # TODO NEed to return no season set message

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            current_event = Event()

        scout_questions = []
        try:
            sqs = ScoutQuestion.objects.filter(Q(season=current_season) & Q(sq_typ_id=question_type))
            for sq in sqs:
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
                    'question_typ': sq.question_typ_id,
                    'question': sq.question,
                    'order': sq.order,
                    'active': sq.active,
                    'void_ind': sq.void_ind,
                    'options': options
                })
        except Exception as e:
            scout_questions = []

        return {'questionTypes': question_types, 'scoutQuestions': scout_questions}

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.get_init(request.query_params.get('sq_typ', None))
                serializer = ScoutAdminQuestionInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing', True, e)
        else:
            return ret_message('You do not have access', True)

class PostSaveScoutFieldQuestionAnswers(APIView):
    """API endpoint to save new questions"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_question(self, data):
        try:
            season = Season.objects.get(current='y')
            sfq = ScoutQuestion(season=season, question_typ_id=data['question_typ'],  sq_typ_id='field',
                               question=data['question'], order=data['order'], active='y', void_ind='n')

            sfq.save()

            for op in data['options']:
                QuestionOptions(option=op['option'], sfq_id=sfq.sq_id, active='y', void_ind='n').save()

            return ret_message('Saved question successfully', False)
        except Exception as e:
            return ret_message('No season set, can\'t save question', True)


    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True)

        if has_access(request.user.id, 2):
            try:
                req = self.save_question(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the question', True, e)
        else:
            return ret_message('You do not have access', True)


class PostUpdateScoutFieldQuestionAnswers(APIView):
    """API endpoint to update questions"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def update_question(self, data):
        print(data)
        sfq = ScoutQuestion.objects.get(sq_id=data['sq_id'])

        sfq.question = data['question']
        sfq.order = data['order']
        sfq.question_typ_id = data['question_typ']
        sfq.save()

        for op in data['options']:
            if op.get('q_opt_id', None) is not None:
                o = QuestionOptions.objects.get(q_opt_id=op['q_opt_id'])
                o.option = op['option']
                o.active = op['active']
                o.save()
            else:
                QuestionOptions(option=op['option'], sq_id=sfq.sq_id, active='y', void_ind='n').save()

        return ret_message('Question saved successfully', False)


    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True)

        if has_access(request.user.id, 2):
            try:
                req = self.update_question(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while updating the question', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutAdminDeleteScoutFieldQuestion(APIView):
    """
    API endpoint to delete a scout field question
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, sfq_id):
        sfq = ScoutQuestion.objects.get(sq_id=sfq_id)

        if sfq.active == 'n':
            sfq.active = 'y'
        else:
            sfq.active = 'n'

        sfq.save()

        return ret_message('Successfully toggled the question')

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.delete(request.query_params.get('sfq_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the scout field question', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutAdminToggleOption(APIView):
    """
    API endpoint to toggle a question option
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def toggle(self, q_opt_id):
        opt = QuestionOptions.objects.get(q_opt_id=q_opt_id)

        if opt.active == 'n':
            opt.active = 'y'
        else:
            opt.active = 'n'

        opt.save()

        return ret_message('Successfully toggled the option')

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.toggle(request.query_params.get('q_opt_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the option', True, e)
        else:
            return ret_message('You do not have access', True)


class PostSaveScoutPitQuestionAnswers(APIView):
    """API endpoint to save new questions"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_question(self, data):
        try:
            season = Season.objects.get(current='y')
            spq = ScoutQuestion(season=season, question_typ_id=data['question_typ'], sq_typ_id='pit',
                               question=data['question'], order=data['order'], active='y', void_ind='n')

            spq.save()

            for op in data['options']:
                QuestionOptions(option=op['option'], spq_id=spq.sq_id, active='y', void_ind='n').save()

            return ret_message('Saved question successfully', False)
        except Exception as e:
            return ret_message('No season set, can\'t save question', True)


    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True)

        if has_access(request.user.id, 2):
            try:
                req = self.save_question(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the question', True, e)
        else:
            return ret_message('You do not have access', True)


class PostUpdateScoutPitQuestionAnswers(APIView):
    """API endpoint to update questions"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def update_question(self, data):
        spq = ScoutQuestion.objects.get(sq_id=data['sq_id'])

        spq.question = data['question']
        spq.order = data['order']
        spq.question_typ_id = data['question_typ']
        spq.save()

        for op in data['options']:
            if op.get('q_opt_id', None) is not None:
                o = QuestionOptions.objects.get(q_opt_id=op['q_opt_id'])
                o.option = op['option']
                o.active = op['active']
                o.save()
            else:
                QuestionOptions(option=op['option'], sq_id=spq.sq_id, active='y', void_ind='n').save()

        return ret_message('Question saved successfully', False)


    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True)

        if has_access(request.user.id, 2):
            try:
                req = self.update_question(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while updating the question', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutAdminDeleteScoutPitQuestion(APIView):
    """
    API endpoint to delete a scout field question
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, spq_id):
        spq = ScoutQuestion.objects.get(sq_id=spq_id)

        if spq.active == 'n':
            spq.active = 'y'
        else:
            spq.active = 'n'

        spq.save()

        return ret_message('Successfully toggled the question')

    def get(self, request, format=None):
        if has_access(request.user.id, 2):
            try:
                req = self.delete(request.query_params.get('sfq_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the scout field question', True, e)
        else:
            return ret_message('You do not have access', True)
