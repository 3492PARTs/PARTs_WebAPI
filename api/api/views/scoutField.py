from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.api.serializers import *
from api.api.models import *
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from api.auth.security import *


class GetScoutFieldInputs(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_questions(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while initializing: no season set', True, e) # TODO NEed to return no season set message

        scout_questions = []
        try:
            sqs = ScoutQuestion.objects.filter(Q(season=current_season) & Q(sq_typ_id='field') & Q(active='y') & Q(void_ind='n')).order_by('order')
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

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('An error occurred while initializing: no event set', True, e) # TODO NEed to return no season set message

        teams = []
        try:
            teams = Team.objects.filter(team_no__in=list(EventTeamXref.objects.filter(event=current_event).values_list('team_no', flat=True))).order_by('team_no')

        except Exception as e:
            teams.append(Team())

        return {'scoutQuestions': scout_questions, 'teams': teams}

    def get(self, request, format=None):
        if has_access(request.user.id, 1):
            try:
                req = self.get_questions()
                serializer = ScoutAnswerSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing', True, e)
        else:
            return ret_message('You do not have access', True)


class PostSaveScoutFieldAnswers(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_answers(self, data):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while saving: no season set', True, e) # TODO NEed to return no season set message

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('An error occurred while saving: no event set', True, e) # TODO NEed to return no season set message

        sf = ScoutField(event=current_event, team_no_id=data['team'], user_id=self.request.user.id, void_ind='n')
        sf.save()

        for d in data['scoutQuestions']:
            sfa = ScoutFieldAnswer(scout_field=sf, sq_id=d['sq_id'], answer=d.get('answer', ''), void_ind='n')
            sfa.save()

        return ret_message('Question saved successfully', False)

    def post(self, request, format=None):
        serializer = ScoutAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True)

        if has_access(request.user.id, 1):
            try:
                req = self.save_answers(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving answers', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutFieldQuery(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_answers(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while getting: no season set', True, e) # TODO NEed to return no season set message

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            current_event = Event()

        scout_cols = [{
                    'PropertyName': 'team',
                    'ColLabel': 'Team No',
                    'order': 0
                }]
        scout_answers = []
        try:
            sqs = ScoutQuestion.objects.filter(Q(season=current_season) & Q(sq_typ_id='field') & Q(active='y') & Q(void_ind='n')).order_by('order')
            for sq in sqs:
                scout_cols.append({
                    'PropertyName': sq.sq_id,
                    'ColLabel': sq.question,
                    'order': sq.order
                })

            scout_cols.append({
                'PropertyName': 'user',
                'ColLabel': 'Scout',
                'order': 9999999999
            })

            sfs = ScoutField.objects.filter(Q(event=current_event) & Q(void_ind='n')).order_by('scout_field_id')
            for sf in sfs:
                sfas = ScoutFieldAnswer.objects.filter(Q(scout_field=sf) & Q(void_ind='n'))

                sa_obj = {}
                for sfa in sfas:
                    sa_obj[sfa.sq_id] = sfa.answer

                sa_obj['user'] = sf.user.first_name + ' ' + sf.user.last_name
                sa_obj['user_id'] = sf.user.id
                sa_obj['team'] = sf.team_no_id
                scout_answers.append(sa_obj)

        except Exception as e:
            scout_cols = []
            scout_answers = []


        return {'scoutCols': scout_cols, 'scoutAnswers': scout_answers}

    def get(self, request, format=None):
        if has_access(request.user.id, 1):
            try:
                req = self.get_answers()
                serializer = ScoutFieldResultsSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing', True, e)
        else:
            return ret_message('You do not have access', True)