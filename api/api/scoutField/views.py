from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from api.api.models import *
from rest_framework.views import APIView
from api.auth.security import *
from .serializers import *

auth_obj = 1 + 48


class GetQuestions(APIView):
    """
    API endpoint to get scout field inputs
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_questions(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'api/scoutField/GetQuestions', self.request.user.id, e)

        scout_questions = []
        try:
            sqs = ScoutQuestion.objects.filter(Q(season=current_season) & Q(sq_typ_id='field') & Q(active='y') &
                                               Q(void_ind='n')).order_by('order')

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
            x = 1

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, 'api/scoutField/GetQuestions', self.request.user.id, e)

        teams = []
        try:
            teams = Team.objects.filter(
                event=current_event).order_by('team_no')

        except Exception as e:
            x = 1

        return {'scoutQuestions': scout_questions, 'teams': teams}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions()

                if type(req) == Response:
                    return req

                serializer = ScoutFieldSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'api/scoutField/GetQuestions',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'api/scoutField/GetQuestions', request.user.id)


class PostSaveAnswers(APIView):
    """
    API endpoint to save scout field answers
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_answers(self, data):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'api/scoutField/PostSaveAnswers', self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin', True, 'api/scoutField/PostSaveAnswers', self.request.user.id, e)

        sf = ScoutField(
            event=current_event, team_no_id=data['team'], user_id=self.request.user.id, void_ind='n')
        sf.save()

        for d in data['scoutQuestions']:
            sfa = ScoutFieldAnswer(
                scout_field=sf, sq_id=d['sq_id'], answer=d.get('answer', ''), void_ind='n')
            sfa.save()

        return ret_message('Question saved successfully')

    def post(self, request, format=None):
        serializer = ScoutFieldSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'api/scoutField/PostSaveAnswers', request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_answers(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving answers.', True, 'api/scoutField/PostSaveAnswers',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'api/scoutField/PostSaveAnswers', request.user.id)


class GetResults(APIView):
    """
    API endpoint to get the results of field scouting
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_answers(self, team):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'api/scoutField/GetResults', self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, 'api/scoutField/GetResults', self.request.user.id, e)

        scout_cols = [{
            'PropertyName': 'team',
            'ColLabel': 'Team No',
            'order': 0
        }]
        scout_answers = []
        try:
            sqs = ScoutQuestion.objects.filter(Q(season=current_season) & Q(
                sq_typ_id='field') & Q(active='y') & Q(void_ind='n')).order_by('order')
            for sq in sqs:
                scout_cols.append({
                    'PropertyName': 'ans' + str(sq.sq_id),
                    'ColLabel': sq.question,
                    'order': sq.order
                })

            scout_cols.append({
                'PropertyName': 'user',
                'ColLabel': 'Scout',
                'order': 9999999999
            })

            if team is not None:
                sfs = ScoutField.objects.filter(Q(event=current_event) & Q(team_no_id=team) & Q(void_ind='n'))\
                    .order_by('scout_field_id')
            else:
                sfs = ScoutField.objects.filter(Q(event=current_event) & Q(
                    void_ind='n')).order_by('scout_field_id')

            for sf in sfs:
                sfas = ScoutFieldAnswer.objects.filter(
                    Q(scout_field=sf) & Q(void_ind='n'))

                sa_obj = {}
                for sfa in sfas:
                    sa_obj['ans' + str(sfa.sq_id)] = sfa.answer

                sa_obj['user'] = sf.user.first_name + ' ' + sf.user.last_name
                sa_obj['user_id'] = sf.user.id
                sa_obj['team'] = sf.team_no_id
                scout_answers.append(sa_obj)

        except Exception as e:
            scout_cols = []
            scout_answers = []

        return {'scoutCols': scout_cols, 'scoutAnswers': scout_answers}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_answers(request.query_params.get('team', None))

                if type(req) == Response:
                    return req

                serializer = ScoutFieldResultsSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'api/scoutField/GetResults',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'api/scoutField/GetResults', request.user.id)
