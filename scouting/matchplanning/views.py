from cloudinary.templatetags import cloudinary
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from general.security import ret_message, has_access
from scouting.field.views import get_field_results
from scouting.matchplanning.serializers import InitSerializer, SaveTeamNoteSerializer, MatchPlanningSerializer, \
    TeamSerializer, TeamNoteSerializer
from scouting.models import Event, Team, Match, ScoutPit, ScoutPitAnswer, ScoutQuestion, Season, ScoutField, \
    ScoutFieldAnswer, TeamNotes
from scouting.pit.views import get_pit_results

auth_obj = 49
app_url = 'scouting/match-planning/'


class Init(APIView):
    """API endpoint to tell the frontend if the competition page is active and its information"""
    endpoint = 'init/'

    def get_competition_information(self):
        current_event = Event.objects.get(Q(current='y') & Q(void_ind='n'))
        team3492 = Team.objects.get(team_no=3492)

        matches = Match.objects.filter(Q(event=current_event) & Q(void_ind='n') &
                                       Q(Q(red_one=team3492) | Q(red_two=team3492) |
                                         Q(red_three=team3492) | Q(blue_one=team3492) | Q(blue_two=team3492) |
                                         Q(blue_three=team3492))) \
            .order_by('comp_level__comp_lvl_order', 'match_number')

        teams = Team.objects.filter(event=current_event).order_by('team_no')

        return {'event': current_event, 'matches': matches, 'teams': teams}

    def get(self, request, format=None):
        try:
            req = self.get_competition_information()
            serializer = InitSerializer(req)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting match information.', True,
                               app_url + self.endpoint, exception=e)


class SaveNote(APIView):
    """API endpoint to tell the frontend if the competition page is active and its information"""
    endpoint = 'save-note/'

    def save_note(self, data):
        current_event = Event.objects.get(Q(current='y') & Q(void_ind='n'))

        note = TeamNotes(event=current_event, team_no_id=data['team_no'], match_id=data.get('match', None),
                         user=self.request.user, note=data['note'])

        note.save()

        return ret_message('Note saved successfully')

    def post(self, request, format=None):
        serializer = SaveTeamNoteSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_note(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving note.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


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

        results = []

        for t in teams:
            # Pit Data
            st = TeamSerializer(t).data
            pit = get_pit_results([st], self.endpoint, self.request)

            if pit.data.get('error', False):
                pit = None

            # Field Data
            team_results = get_field_results(t, self.endpoint, self.request)
            field_cols = team_results['scoutCols']
            field_answers = team_results['scoutAnswers']

            # notes
            notes = TeamNotes.objects.filter(Q(void_ind='n') & Q(team_no=t)).order_by('-time')

            results.append({'team': t,
                            'pitData': pit,
                            'fieldCols': field_cols,
                            'fieldAnswers': field_answers,
                            'notes': notes})
        return results

    def get(self, request, format=None):
        try:
            req = self.get_match_information(request.query_params.get('match_id', None))
            serializer = MatchPlanningSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting match information.', True,
                               app_url + self.endpoint, exception=e)


class LoadTeamNotes(APIView):
    """API endpoint to get team notes"""
    endpoint = 'load-team-notes/'

    def get_team_notes(self, team_no):
        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, app_url + self.endpoint, self.request.user.id, e)

        try:
            current_event = Event.objects.get(
                Q(season=current_season) & Q(current='y'))
        except Exception as e:
            return ret_message('No event set, see an admin', True, app_url + self.endpoint, self.request.user.id, e)

        team = Team.objects.get(Q(void_ind='n') & Q(team_no=team_no))
        notes = TeamNotes.objects.filter(Q(void_ind='n') & Q(team_no=team) & Q(event=current_event))\
            .order_by('-time')
        return notes

    def get(self, request, format=None):
        try:
            req = self.get_team_notes(request.query_params.get('team_no', None))
            serializer = TeamNoteSerializer(req, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting team notes.', True,
                               app_url + self.endpoint, exception=e)