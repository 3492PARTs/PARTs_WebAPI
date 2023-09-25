from datetime import datetime

from pytz import utc
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import form.util
from form.models import Question, QuestionAnswer
from scouting.models import Season, Event, Team, ScoutFieldSchedule, ScoutField, \
    EventTeamInfo, Match
from rest_framework.views import APIView
from general.security import ret_message, has_access
from .serializers import ScoutFieldSerializer, ScoutFieldResultsSerializer, SaveScoutFieldSerializer
from django.db.models import Q
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings

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

        scout_questions = form.util.get_questions('field')

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

        matches = Match.objects.filter(Q(event=current_event) & Q(comp_level_id='qm') & Q(void_ind='n')) \
            .order_by('match_number')
        parsed_matches = []

        for m in matches:
            parsed_matches.append({
                'match_id': m.match_id,
                'event_id': m.event.event_id,
                'match_number': m.match_number,
                'time': m.time,
                'blue_one_id': m.blue_one.team_no if self.get_team_match_field_result(m, m.blue_one.team_no) is None else None,
                'blue_two_id': m.blue_two.team_no if self.get_team_match_field_result(m, m.blue_two.team_no) is None else None,
                'blue_three_id': m.blue_three.team_no if self.get_team_match_field_result(m, m.blue_three.team_no) is None else None,
                'red_one_id': m.red_one.team_no if self.get_team_match_field_result(m, m.red_one.team_no) is None else None,
                'red_two_id': m.red_two.team_no if self.get_team_match_field_result(m, m.red_two.team_no) is None else None,
                'red_three_id': m.red_three.team_no if self.get_team_match_field_result(m, m.red_three.team_no) is None else None,
            })

        return {'scoutQuestions': scout_questions, 'teams': teams, 'scoutFieldSchedule': sfs, 'matches': parsed_matches}

    def get_team_match_field_result(self, m, team):
        try:
            res = ScoutField.objects.filter(Q(match=m) & Q(team_no=team) & Q(void_ind='n'))
            if res.count() > 0:
                return res
            else:
                return None
        except:
            x = 9

        return None

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


class Results(APIView):
    """
    API endpoint to get the results of field scouting
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'results/'

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj) or has_access(request.user.id, auth_view_obj):
            try:
                req = get_field_results(request.query_params.get('team', None), self.endpoint, self.request)

                if type(req) == Response:
                    return req

                serializer = ScoutFieldResultsSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


def get_field_results(team, endpoint, request):
    try:
        current_season = Season.objects.get(current='y')
    except Exception as e:
        return ret_message('No season set, see an admin.', True, app_url + endpoint, request.user.id, e)

    try:
        current_event = Event.objects.get(
            Q(season=current_season) & Q(current='y') & Q(void_ind='n'))
    except Exception as e:
        return ret_message('No event set, see an admin.', True, app_url + endpoint, request.user.id, e)

    scout_cols = [{
        'PropertyName': 'team',
        'ColLabel': 'Team No',
        'order': 0
    }, {
        'PropertyName': 'rank',
        'ColLabel': 'Rank',
        'order': 1
    }, {
        'PropertyName': 'match',
        'ColLabel': 'Match',
        'order': 1
    }]

    scout_answers = []
    sqsa = Question.objects.filter(Q(season=current_season) & Q(form_typ_id='field') &
                                        Q(form_sub_typ_id='auto') & Q(active='y') & Q(void_ind='n')).order_by('order')

    sqst = Question.objects.filter(Q(season=current_season) & Q(form_typ_id='field') &
                                        Q(form_sub_typ_id='teleop') & Q(active='y') & Q(void_ind='n')) \
        .order_by('order')

    sqso = Question.objects.filter(Q(season=current_season) & Q(form_typ_id='field') &
                                        Q(form_sub_typ_id__isnull=True) & Q(active='y') & Q(void_ind='n')) \
        .order_by('order')

    for sqs in [sqsa, sqst, sqso]:
        for sq in sqs:
            scout_cols.append({
                'PropertyName': 'ans' + str(sq.question_id),
                'ColLabel': ('' if sq.form_sub_typ is None else sq.form_sub_typ.form_sub_typ[
                                                              0:1].upper() + ': ') + sq.question,
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
        # get result for individual team
        sfs = ScoutField.objects.filter(Q(event=current_event) & Q(team_no_id=team) & Q(void_ind='n')) \
            .order_by('-time', '-scout_field_id')
    else:
        # get result for all teams
        if settings.DEBUG:
            sfs = ScoutField.objects.filter(Q(event=current_event) & Q(
                void_ind='n')).order_by('-time', '-scout_field_id')[: 10]
        else:
            sfs = ScoutField.objects.filter(Q(event=current_event) & Q(
            void_ind='n')).order_by('-time', '-scout_field_id')

    for sf in sfs:
        sfas = QuestionAnswer.objects.filter(
            Q(scout_field=sf) & Q(void_ind='n'))

        sa_obj = {}
        for sfa in sfas:
            sa_obj['ans' + str(sfa.question_id)] = sfa.answer

        sa_obj['match'] = sf.match.match_number if sf.match else None
        sa_obj['user'] = sf.user.first_name + ' ' + sf.user.last_name
        sa_obj['time'] = sf.time
        sa_obj['user_id'] = sf.user.id
        sa_obj['team'] = sf.team_no_id

        try:
            eti = EventTeamInfo.objects.get(Q(event=current_event) & Q(team_no=sf.team_no) & Q(void_ind='n'))
            sa_obj['rank'] = eti.rank
        except:
            x = 1

        scout_answers.append(sa_obj)

    return {'scoutCols': scout_cols, 'scoutAnswers': scout_answers}
