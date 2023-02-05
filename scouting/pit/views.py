from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from scouting.models import ScoutQuestion, QuestionOptions, Season, Team, Event, ScoutPit, ScoutPitAnswer
from .serializers import InitSerializer, PitTeamDataSerializer, ScoutAnswerSerializer, ScoutPitResultsSerializer
from scouting.admin.serializers import ScoutQuestionSerializer
from scouting.field.serializers import TeamSerializer
from rest_framework.views import APIView
from general.security import ret_message,  has_access
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.db.models import Q, Prefetch
from rest_framework.response import Response

auth_obj = 51
auth_view_obj = 53
app_url = 'scouting/pit/'


class Questions(APIView):
    """
    API endpoint to get scout pit inputs
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'questions/'

    def get_questions(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        scout_questions = []
        try:
            scout_questions = ScoutQuestion.objects.prefetch_related('questionoptions_set').filter(
                Q(season=current_season) & Q(sq_typ_id='pit') & Q(active='y') & Q(void_ind='n')).order_by('order')
        except Exception as e:
            x = 1

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        teams = []
        try:
            teams = Team.objects.filter(Q(event=current_event) &
                                        ~Q(team_no__in=(
                                            ScoutPit.objects.filter(Q(event=current_event) & Q(void_ind='n')).values_list('team_no', flat=True)))
                                        ).order_by('team_no')
        except Exception as e:
            teams.append(Team())

        comp_teams = []
        try:
            comp_teams = Team.objects.filter(
                Q(event=current_event) &
                Q(team_no__in=(ScoutPit.objects.filter(
                    Q(event=current_event) & Q(void_ind='n')).values_list('team_no', flat=True)))
            ).order_by('team_no')
        except Exception as e:
            comp_teams.append(Team())

        return {'scoutQuestions': scout_questions, 'teams': teams, 'comp_teams': comp_teams}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions()

                if type(req) == Response:
                    return req

                serializer = InitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SaveAnswers(APIView):
    """
    API endpoint to save scout pit answers
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

        try:
            sp = ScoutPit.objects.get(team_no_id=data['team'])
        except Exception as e:
            sp = ScoutPit(
                event=current_event, team_no_id=data['team'], user_id=self.request.user.id, void_ind='n')
            sp.save()

        for d in data['scoutQuestions']:
            try:
                spa = ScoutPitAnswer.objects.get(
                    Q(scout_pit=sp) & Q(sq_id=d['sq_id']))
                spa.answer = d.get('answer', '')
            except Exception as e:
                spa = ScoutPitAnswer(scout_pit=sp, sq_id=d['sq_id'],
                                     answer=d.get('answer', ''), void_ind='n')
            spa.save()

        return ret_message('Response saved successfully')

    def post(self, request, format=None):
        serializer = ScoutAnswerSerializer(data=request.data)
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


class SavePicture(APIView):
    """
    API endpoint to save a robot picture
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-picture/'

    def save_file(self, file, team_no):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        if not allowed_file(file.name):
            return ret_message('Invalid file type.', True, app_url + self.endpoint, self.request.user.id)

        try:
            response = cloudinary.uploader.upload(file)
            sp = ScoutPit.objects.get(
                Q(event=current_event) & Q(team_no_id=team_no))

            sp.img_id = response['public_id']
            sp.img_ver = str(response['version'])
            sp.save()
        except Exception as e:
            return ret_message('An error occurred while saving the image.', True, app_url + self.endpoint,
                               self.request.user.id, e)

        return ret_message('Saved Image Successfully.')

    def post(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                file_obj = request.FILES['file']
                ret = self.save_file(file_obj, request.data.get('team_no', ''))
                return ret
            except Exception as e:
                return ret_message('An error occurred while saving robot picture.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class ResultsInit(APIView):
    """
    API endpoint to get the teams who have already been scouted
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'results-init/'

    def get_teams(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        teams = []
        try:
            teams = Team.objects.filter(
                Q(event=current_event) &
                Q(team_no__in=(list(
                    ScoutPit.objects.filter(Q(event=current_event) & Q(void_ind='n')).values_list('team_no',
                                                                                                  flat=True))))
            ).order_by('team_no')

        except Exception as e:
            x = 1

        return teams

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj) or has_access(request.user.id, auth_view_obj):
            try:
                req = self.get_teams()
                serializer = TeamSerializer(req, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class Results(APIView):
    """
    API endpoint to get scout pit results for the selected teams
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'results/'

    def get_results(self, teams):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin', True, app_url + self.endpoint, self.request.user.id, e)

        results = []
        for t in teams:
            if t.get('checked', False):
                team = Team.objects.get(team_no=t['team_no'])
                try:
                    sp = ScoutPit.objects.get(Q(team_no_id=t['team_no']) & Q(
                        event=current_event) & Q(void_ind='n'))
                except Exception as e:
                    return ret_message('No pit data for team.', True, app_url + self.endpoint,
                                       self.request.user.id, e)

                spas = ScoutPitAnswer.objects.filter(
                    Q(scout_pit=sp) & Q(void_ind='n'))

                tmp = {
                    'teamNo': team.team_no,
                    'teamNm': team.team_nm,
                    'pic': cloudinary.CloudinaryImage(sp.img_id, version=sp.img_ver).build_url(),
                }

                tmp_questions = []
                for spa in spas:
                    sq = ScoutQuestion.objects.get(sq_id=spa.sq_id)
                    tmp_questions.append({
                        'question': sq.question,
                        'answer': spa.answer
                    })

                tmp['results'] = tmp_questions
                results.append(tmp)

        return results

    def post(self, request, format=None):
        if has_access(request.user.id, auth_obj) or has_access(request.user.id, auth_view_obj):
            try:
                serializer = TeamSerializer(data=request.data, many=True)
                if not serializer.is_valid():
                    return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                                       serializer.errors)

                ret = self.get_results(serializer.data)

                if type(ret) == Response:
                    return ret

                serializer = ScoutPitResultsSerializer(ret, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while getting pit results.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class TeamData(APIView):
    """
    API endpoint to get scout pit team data
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'team-data/'

    def get_questions(self, team_num):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        sp = ScoutPit.objects.get(team_no=team_num)

        scout_questions = []
        # sqs = ScoutQuestion.objects.prefetch_related('questionoptions_set').filter(
        #    Q(season=current_season) & Q(sq_typ_id='pit') & Q(active='y') & Q(void_ind='n')).order_by('order')
        sqs = ScoutQuestion.objects\
            .prefetch_related(Prefetch('questionoptions_set'), Prefetch('scoutpitanswer_set', queryset=ScoutPitAnswer.objects.filter(Q(scout_pit=sp)).select_related('sq')))\
            .filter(Q(season=current_season) & Q(sq_typ_id='pit') & Q(active='y') & Q(void_ind='n')).order_by('order')

        for sq in sqs:
            try:
                spa = ScoutPitAnswer.objects.get(
                    Q(scout_pit=sp) & Q(sq=sq))
            except Exception as e:
                spa = ScoutPitAnswer(answer='')

            scout_questions.append({
                'sq_id': sq.sq_id,
                'season': sq.season,
                'sq_typ': sq.sq_typ,
                'question_typ': sq.question_typ,
                'question': sq.question,
                'order': sq.order,
                'active': sq.active,
                'void_ind': sq.void_ind,
                'questionoptions_set': sq.questionoptions_set,
                'answer': spa.answer
            })
        return {'questions': scout_questions, 'pic': cloudinary.CloudinaryImage(sp.img_id, version=sp.img_ver).build_url()}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions(
                    request.query_params.get('team_num', None))
                serializer = PitTeamDataSerializer(req,)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while getting team data.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


def allowed_file(filename):
    """Returns whether a filename's extension indicates that it is an image.
    :param str filename: A filename.
    :return: Whether the filename has an recognized image file extension
    :rtype: bool"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}