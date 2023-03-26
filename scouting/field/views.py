from datetime import datetime

from pytz import utc
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from scouting.models import Season, ScoutQuestion, QuestionOptions, Event, Team, ScoutFieldSchedule, ScoutField, \
    ScoutFieldAnswer, EventTeamInfo
from rest_framework.views import APIView
from general.security import ret_message, has_access
from .serializers import ScoutFieldSerializer, ScoutFieldResultsSerializer
from django.db.models import Q
from rest_framework.response import Response
from django.utils import timezone

auth_obj = 49
auth_view_obj = 52
app_url = 'scouting/field/'


class Questions(APIView):
    """
    API endpoint to get scout field inputs
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'get-questions/'

    def get_questions(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        scout_questions = []
        sqs = ScoutQuestion.objects.prefetch_related('questionoptions_set').filter(Q(season=current_season) & Q(sq_typ_id='field') & Q(active='y') &
                                                                                               Q(void_ind='n')).order_by('sq_sub_typ_id', 'order')

        for sq in sqs:
            scout_questions.append({
                'sq_id': sq.sq_id,
                'season_id': sq.season_id,
                'question': sq.question,
                'order': sq.order,
                'active': sq.active,
                'question_typ': sq.question_typ.question_typ if sq.question_typ is not None else None,
                'question_typ_nm': sq.question_typ.question_typ_nm if sq.question_typ is not None else None,
                'sq_sub_typ': sq.sq_sub_typ.sq_sub_typ if sq.sq_sub_typ is not None else None,
                'sq_sub_nm': sq.sq_sub_typ.sq_sub_nm if sq.sq_sub_typ is not None else None,
                'sq_typ': sq.sq_typ,
                'questionoptions_set': sq.questionoptions_set
            })

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        teams = []
        teams = Team.objects.filter(
            event=current_event).order_by('team_no')

        sfss = ScoutFieldSchedule.objects.filter(Q(st_time__lte=timezone.now()) & Q(
            end_time__gte=timezone.now()) & Q(void_ind='n'))

        sfs = None
        for s in sfss:
            sfs = {
                'scout_field_sch_id': s.scout_field_sch_id,
                'event_id': s.event_id,
                'st_time': s.st_time,
                'end_time': s.end_time,
                'red_one_id': s.red_one,
                'red_two_id': s.red_two,
                'red_three_id': s.red_three,
                'blue_one_id': s.blue_one,
                'blue_two_id': s.blue_two,
                'blue_three_id': s.blue_three
            }

        return {'scoutQuestions': scout_questions, 'teams': teams, 'scoutFieldSchedule': sfs}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions()

                if type(req) == Response:
                    return req

                serializer = ScoutFieldSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SaveAnswers(APIView):
    """
    API endpoint to save scout field answers
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-answers/'

    def save_answers(self, data):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin', True, app_url + self.endpoint, self.request.user.id, e)

        sf = ScoutField(
            event=current_event, team_no_id=data['team'], user_id=self.request.user.id, void_ind='n')
        sf.save()

        for d in data['scoutQuestions']:
            sfa = ScoutFieldAnswer(
                scout_field=sf, sq_id=d['sq_id'], answer=d.get('answer', ''), void_ind='n')
            sfa.save()

        return ret_message('Response saved successfully')

    def post(self, request, format=None):
        serializer = ScoutFieldSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_answers(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving answers.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class Results(APIView):
    """
    API endpoint to get the results of field scouting
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'results/'

    def get_answers(self, team):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        scout_cols = [{
            'PropertyName': 'team',
            'ColLabel': 'Team No',
            'order': 0
        }, {
            'PropertyName': 'rank',
            'ColLabel': 'Rank',
            'order': 1
        }]

        scout_answers = []
        sqsa = ScoutQuestion.objects.filter(Q(season=current_season) & Q(sq_typ_id='field') &
                                            Q(sq_sub_typ_id='auto') & Q(active='y') & Q(void_ind='n')).order_by('order')

        sqst = ScoutQuestion.objects.filter(Q(season=current_season) & Q(sq_typ_id='field') &
                                            Q(sq_sub_typ_id='teleop') & Q(active='y') & Q(void_ind='n'))\
            .order_by('order')

        sqso = ScoutQuestion.objects.filter(Q(season=current_season) & Q(sq_typ_id='field') &
                                            Q(sq_sub_typ_id__isnull=True) & Q(active='y') & Q(void_ind='n'))\
            .order_by('order')

        for sqs in [sqsa, sqst, sqso]:
            for sq in sqs:
                scout_cols.append({
                    'PropertyName': 'ans' + str(sq.sq_id),
                    'ColLabel': ('' if sq.sq_sub_typ is None else sq.sq_sub_typ.sq_sub_typ[0:1].upper() + ': ') + sq.question,
                    'order': sq.order
                })

        scout_cols.append({
            'PropertyName': 'user',
            'ColLabel': 'Scout',
            'order': 9999999999
        })
        scout_cols.append({
            'PropertyName': 'time',
            'ColLabel': 'Time',
            'order': 99999999999
        })

        if team is not None:
            sfs = ScoutField.objects.filter(Q(event=current_event) & Q(team_no_id=team) & Q(void_ind='n')) \
                .order_by('-time', '-scout_field_id')
        else:
            sfs = ScoutField.objects.filter(Q(event=current_event) & Q(
                void_ind='n')).order_by('-time', '-scout_field_id')

        for sf in sfs:
            sfas = ScoutFieldAnswer.objects.filter(
                Q(scout_field=sf) & Q(void_ind='n'))

            sa_obj = {}
            for sfa in sfas:
                sa_obj['ans' + str(sfa.sq_id)] = sfa.answer

            sa_obj['user'] = sf.user.first_name + ' ' + sf.user.last_name
            sa_obj['time'] = sf.time
            sa_obj['user_id'] = sf.user.id
            sa_obj['team'] = sf.team_no_id

            eti = EventTeamInfo.objects.get(Q(event=current_event) & Q(team_no=sf.team_no) & Q(void_ind='n'))
            sa_obj['rank'] = eti.rank

            scout_answers.append(sa_obj)

        return {'scoutCols': scout_cols, 'scoutAnswers': scout_answers}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj) or has_access(request.user.id, auth_view_obj):
            try:
                req = self.get_answers(request.query_params.get('team', None))

                if type(req) == Response:
                    return req

                serializer = ScoutFieldResultsSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)
