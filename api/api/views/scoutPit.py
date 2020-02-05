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
import cloudinary
import cloudinary.uploader
import cloudinary.api

class GetScoutPitInputs(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_questions(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while initializing: no season set', True,
                               e)  # TODO NEed to return no season set message

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
            scout_questions = []

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('An error occurred while initializing: no event set', True,
                               e)  # TODO NEed to return no season set message

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
        if has_access(request.user.id, 1):
            try:
                req = self.get_questions()
                serializer = ScoutAnswerSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing', True, e)
        else:
            return ret_message('You do not have access', True)


class PostSaveScoutPitAnswers(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_answers(self, data):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while saving: no season set', True,
                               e)  # TODO NEed to return no season set message

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('An error occurred while saving: no event set', True,
                               e)  # TODO NEed to return no season set message

        sp = ScoutPit(event=current_event, team_no_id=data['team'], user_id=self.request.user.id, void_ind='n')
        sp.save()

        for d in data['scoutQuestions']:
            spa = ScoutPitAnswer(scout_pit=sp, sq_id=d['sq_id'],
                                 answer=d.get('answer', ''), void_ind='n')
            spa.save()

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


class PostSaveScoutPitPicture(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_file(self, file, team_no):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while saving: no season set', True,
                               e)  # TODO NEed to return no season set message

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('An error occurred while saving: no event set', True,
                               e)  # TODO NEed to return no season set message

        if not allowed_file(file.name):
            return ret_message('Invalid file type', True)

        try:
            response = cloudinary.uploader.upload(file)
            sp = ScoutPit.objects.get(Q(event=current_event) & Q(team_no_id=team_no))

            sp.img_id = response['public_id']
            sp.img_ver = str(response['version'])
            sp.save()
        except Exception as e:
            return ret_message('An error occurred while saving image', True,
                               e)  # TODO NEed to return no season set message

        return ret_message('Save Image Successfully.', True)

    def post(self, request, format=None):
        if has_access(request.user.id, 1):
            try:
                file_obj = request.FILES['file']
                ret = self.save_file(file_obj, request.data.get('team_no', ''))
                return ret
            except Exception as e:
                return ret_message('An error occurred while saving robot picture', True, e)
        else:
            return ret_message('You do not have access', True)


class GetScoutPitResultInit(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_teams(self):

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while initializing: no season set', True,
                               e)  # TODO NEed to return no season set message

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('An error occurred while initializing: no event set', True,
                               e)  # TODO NEed to return no season set message

        teams = []
        try:
            teams = Team.objects.filter(
                Q(team_no__in=list(EventTeamXref.objects.filter(event=current_event).values_list('team_no', flat=True))) &
                Q(team_no__in=(list(ScoutPit.objects.filter(Q(event=current_event) & Q(void_ind='n')).values_list('team_no', flat=True))))
            ).order_by('team_no')

        except Exception as e:
            teams.append(Team())

        return teams

    def get(self, request, format=None):
        if has_access(request.user.id, 1):
            try:
                req = self.get_teams()
                serializer = TeamSerializer(req, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing', True, e)
        else:
            return ret_message('You do not have access', True)


class PostGetScoutPitResults(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_results(self, teams):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('An error occurred while saving: no season set', True,
                               e)  # TODO NEed to return no season set message

        try:
            current_event = Event.objects.get(Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('An error occurred while saving: no event set', True,
                               e)  # TODO NEed to return no season set message

        results = []
        for t in teams:
            if t.get('checked', False):
                sp = ScoutPit.objects.get(Q(team_no_id=t['team_no']) & Q(event=current_event) & Q(void_ind='n'))
                spas = ScoutPitAnswer.objects.filter(Q(scout_pit=sp) & Q(void_ind='n'))

                tmp = {
                    'teamNo': t['team_no'],
                    'teamNm': t['team_nm'],
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
        if has_access(request.user.id, 1):
            try:
                serializer = TeamSerializer(data=request.data, many=True)
                if not serializer.is_valid():
                    return ret_message('Invalid data', True)

                ret = self.get_results(serializer.data)
                serializer = ScoutPitResultsSerializer(ret, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while getting pit results.', True, e)
        else:
            return ret_message('You do not have access', True)


def allowed_file(filename):
    '''Returns whether a filename's extension indicates that it is an image.
    :param str filename: A filename.
    :return: Whether the filename has an recognized image file extension
    :rtype: bool'''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
