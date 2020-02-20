from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.api.serializers import *
from api.api.models import *
from rest_framework.views import APIView
from api.auth.security import *
import cloudinary
import cloudinary.uploader
import cloudinary.api

auth_obj = 3


class GetScoutPitInputs(APIView):
    """
    API endpoint to get scout pit inputs
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_questions(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'GetScoutPitInputs', self.request.user.id, e)

        scout_questions = []
        try:
            sqs = ScoutQuestion.objects.filter(
                Q(season=current_season) & Q(sq_typ_id='pit') & Q(active='y') & Q(void_ind='n')).order_by('order')

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
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, 'GetScoutPitInputs', self.request.user.id, e)

        teams = []
        try:
            teams = Team.objects.filter(
                Q(team_no__in=list(EventTeamXref.objects.filter(event=current_event).values_list('team_no', flat=True))) &
                ~Q(team_no__in=(list(ScoutPit.objects.filter(Q(event=current_event) & Q(void_ind='n')).values_list('team_no', flat=True))))
            ).order_by('team_no')

        except Exception as e:
            teams.append(Team())

        return {'scoutQuestions': scout_questions, 'teams': teams}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_questions()
                serializer = ScoutAnswerSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'GetScoutPitInputs',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutPitInputs', request.user.id)


class PostScoutPitSaveAnswers(APIView):
    """
    API endpoint to save scout pit answers
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_answers(self, data):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'PostScoutPitSaveAnswers', self.request.user.id, e)

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin', True, 'PostScoutPitSaveAnswers', self.request.user.id, e)

        sp = ScoutPit(event=current_event, team_no_id=data['team'], user_id=self.request.user.id, void_ind='n')
        sp.save()

        for d in data['scoutQuestions']:
            spa = ScoutPitAnswer(scout_pit=sp, sq_id=d['sq_id'],
                                 answer=d.get('answer', ''), void_ind='n')
            spa.save()

        return ret_message('Question saved successfully')

    def post(self, request, format=None):
        serializer = ScoutAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'PostScoutAdminSaveAnswers', request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_answers(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving answers.', True, 'PostScoutAdminSaveAnswers',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutAdminSaveAnswers', request.user.id)


class PostScoutPitSavePicture(APIView):
    """
    API endpoint to save a robot picture
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_file(self, file, team_no):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'PostScoutPitSavePicture', self.request.user.id, e)

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, 'PostScoutPitSavePicture', self.request.user.id, e)

        if not allowed_file(file.name):
            return ret_message('Invalid file type.', True, 'PostScoutPitSavePicture', self.request.user.id)

        try:
            response = cloudinary.uploader.upload(file)
            sp = ScoutPit.objects.get(Q(event=current_event) & Q(team_no_id=team_no))

            sp.img_id = response['public_id']
            sp.img_ver = str(response['version'])
            sp.save()
        except Exception as e:
            return ret_message('An error occurred while saving the image.', True, 'PostScoutPitSavePicture',
                               self.request.user.id, e)

        return ret_message('Save Image Successfully.')

    def post(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                file_obj = request.FILES['file']
                ret = self.save_file(file_obj, request.data.get('team_no', ''))
                return ret
            except Exception as e:
                return ret_message('An error occurred while saving robot picture.', True, 'PostScoutPitSavePicture',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutPitSavePicture', request.user.id)


class GetScoutPitResultInit(APIView):
    """
    API endpoint to get the teams who have already been scouted
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_teams(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'GetScoutPitResultsInit', self.request.user.id, e)

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin.', True, 'GetScoutPitResultsInit', self.request.user.id, e)

        teams = []
        try:
            teams = Team.objects.filter(
                Q(team_no__in=list(EventTeamXref.objects.filter(event=current_event).values_list('team_no', flat=True))) &
                Q(team_no__in=(list(ScoutPit.objects.filter(Q(event=current_event) & Q(void_ind='n')).values_list('team_no', flat=True))))
            ).order_by('team_no')

        except Exception as e:
            x = 1

        return teams

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_teams()
                serializer = TeamSerializer(req, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'GetScoutPitResultsInit',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutPitResultsInit', request.user.id)


class PostScoutPitGetResults(APIView):
    """
    API endpoint to get scout pit results for the selected teams
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_results(self, teams):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'PostScoutPitGetResults', self.request.user.id, e)

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin', True, 'PostScoutPitGetResults', self.request.user.id, e)

        results = []
        for t in teams:
            if t.get('checked', False):
                team = Team.objects.get(team_no=t['team_no'])
                sp = ScoutPit.objects.get(Q(team_no_id=t['team_no']) & Q(event=current_event) & Q(void_ind='n'))
                spas = ScoutPitAnswer.objects.filter(Q(scout_pit=sp) & Q(void_ind='n'))

                tmp = {
                    'teamNo': team.team_no,
                    'teamNm': team.team_nm,
                    'pic': cloudinary.CloudinaryImage(sp.img_id, version=sp.img_ver).build_url(),
                }

                tmp_questions = []
                for spa in spas:
                    sq = ScoutQuestion.objects.get(sq_id=spa.sq_id)
                    tmp_questions.append({
                        'question':  sq.question,
                        'answer': spa.answer
                    })

                tmp['results'] = tmp_questions
                results.append(tmp)

        return results

    def post(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                serializer = TeamSerializer(data=request.data, many=True)
                if not serializer.is_valid():
                    return ret_message('Invalid data', True, 'PostScoutPitGetResults', request.user.id,
                                       serializer.errors)

                ret = self.get_results(serializer.data)
                serializer = ScoutPitResultsSerializer(ret, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while getting pit results.', True, 'PostScoutPitGetResults',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutPitGetResults', request.user.id)


def allowed_file(filename):
    """Returns whether a filename's extension indicates that it is an image.
    :param str filename: A filename.
    :return: Whether the filename has an recognized image file extension
    :rtype: bool"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
