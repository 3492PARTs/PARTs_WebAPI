from cloudinary.templatetags import cloudinary
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from general.security import ret_message
from scouting.matchPlanning.serializers import InitSerializer
from scouting.models import Event, Team, Match, ScoutPit, ScoutPitAnswer, ScoutQuestion, Season, ScoutField, \
    ScoutFieldAnswer

app_url = 'scouting/match-planning/'


class Init(APIView):
    """API endpoint to tell the frontend if the competition page is active and its information"""
    endpoint = 'init/'

    def get_competition_information(self):
        try:
            event = Event.objects.get(Q(current='y') & Q(
                competition_page_active='y') & Q(void_ind='n'))
            team3492 = Team.objects.get(team_no=3492)

            matches = Match.objects.filter(Q(event=event) & Q(void_ind='n') & Q(Q(red_one=team3492) | Q(red_two=team3492) | Q(
                red_three=team3492) | Q(blue_one=team3492) | Q(blue_two=team3492) | Q(blue_three=team3492))).order_by('comp_level__comp_lvl_order', 'match_number')
        except Exception as e:
            event = None
            matches = None

        return {'event': event, 'matches': matches}

    def get(self, request, format=None):
        try:
            req = self.get_competition_information()
            serializer = InitSerializer(req)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting match information.', True,
                               app_url + self.endpoint, exception=e)


class PlanMatch(APIView):
    """API endpoint to tell the frontend if the competition page is active and its information"""
    endpoint = 'plan-match/'

    def get_match_information(self, match_id):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin', True, app_url + self.endpoint, self.request.user.id, e)

        match = Match.objects.get(match_id=match_id)

        teams = [match.red_one, match.red_two, match.red_three, match.blue_one, match.blue_two, match.blue_three]

        team_info = []

        for t in teams:
            #Pit Data
            team = Team.objects.get(team_no=t['team_no'])
            try:
                sp = ScoutPit.objects.get(Q(team_no_id=t['team_no']) & Q(
                    event=current_event) & Q(void_ind='n'))
            except Exception as e:
                return ret_message('No pit data for team.', True, app_url + self.endpoint,
                                   self.request.user.id, e)

            spas = ScoutPitAnswer.objects.filter(
                Q(scout_pit=sp) & Q(void_ind='n'))

            pit = {
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

            pit['results'] = tmp_questions

            #Field Data
            field_cols = [{
                'PropertyName': 'team',
                'ColLabel': 'Team No',
                'order': 0
            }]
            field_answers = []
            try:
                sqs = ScoutQuestion.objects.filter(Q(season=current_season) & Q(
                    sq_typ_id='field') & Q(active='y') & Q(void_ind='n')).order_by('sq_sub_typ_id', 'order')
                for sq in sqs:
                    field_cols.append({
                        'PropertyName': 'ans' + str(sq.sq_id),
                        'ColLabel': sq.question,
                        'order': sq.order
                    })

                field_cols.append({
                    'PropertyName': 'user',
                    'ColLabel': 'Scout',
                    'order': 9999999999
                })

                sfs = ScoutField.objects.filter(Q(event=current_event) & Q(team_no_id=team) & Q(void_ind='n')) \
                    .order_by('-time')

                for sf in sfs:
                    sfas = ScoutFieldAnswer.objects.filter(
                        Q(scout_field=sf) & Q(void_ind='n'))

                    sa_obj = {}
                    for sfa in sfas:
                        sa_obj['ans' + str(sfa.sq_id)] = sfa.answer

                    sa_obj['user'] = sf.user.first_name + ' ' + sf.user.last_name
                    sa_obj['user_id'] = sf.user.id
                    sa_obj['team'] = sf.team_no_id
                    field_answers.append(sa_obj)

            except Exception as e:
                field_cols = []
                field_answers = []

            results.append(tmp)

    def get(self, request, format=None):
        try:
            req = self.get_match_information(request.query_params.get('match_id', None))
            serializer = CompetitionInformationSerializer(req)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting match information.', True,
                               app_url + self.endpoint, exception=e)