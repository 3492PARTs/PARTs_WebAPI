import datetime

import pytz
from django.db import IntegrityError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.utils import json

from api.api.serializers import *
from api.auth.serializers import PhoneTypeSerializer
from api.api.models import *
from api.auth import send_email
from rest_framework.views import APIView
from api.auth.security import *
import requests

auth_obj = 2


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

        users = AuthUser.objects.filter(Q(is_active=True) & Q(date_joined__isnull=False) &
                                        ~Q(id__in=list(AuthUserGroups.objects
                                                       .filter(group=AuthGroup.objects.get(name='sysadmin'))
                                                       .values_list('user_id', flat=True)
                                                       )
                                           )
                                        )

        user_groups = []
        try:
            user_groups = AuthGroup.objects.filter(id__in=list(ScoutAuthGroups.objects.all().values_list('auth_group_id', flat=True)))
        except Exception as e:
            user_groups = []

        phone_types = PhoneType.objects.all()

        time = timezone.now()  # datetime.now() - timedelta(hours=5) # datetime.now(pytz.timezone('US/Eastern'))
        fieldSchedule = []
        sss = ScoutSchedule.objects.filter(Q(sq_typ_id='field') &
                                           (Q(st_time__gte=time) | (Q(st_time__lte=time) & Q(end_time__gte=time))) &
                                           Q(void_ind='n')
                                           )\
            .order_by('st_time', 'user')
        for ss in sss:
            fieldSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'st_time': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified,
                'void_ind': ss.void_ind,
                'st_time_str': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time_str': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
            })

        pitSchedule = []
        sss = ScoutSchedule.objects.filter(Q(sq_typ_id='pit') &
                                           (Q(st_time__gte=time) | (Q(st_time__lte=time) & Q(end_time__gte=time))) &
                                           Q(void_ind='n')
                                           )\
            .order_by('st_time', 'user')
        for ss in sss:
            pitSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'st_time': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified,
                'void_ind': ss.void_ind,
                'st_time_str': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time_str': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
            })

        pastSchedule = []
        sss = ScoutSchedule.objects.filter(Q(end_time__lt=time) & Q(void_ind='n')).order_by('st_time', 'user')
        for ss in sss:
            pastSchedule.append({
                'scout_sch_id': ss.scout_sch_id,
                'user': ss.user.first_name + ' ' + ss.user.last_name,
                'user_id': ss.user.id,
                'sq_typ': ss.sq_typ_id,
                'sq_nm': ss.sq_typ.sq_nm,
                'st_time': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'notified': ss.notified,
                'void_ind': ss.void_ind,
                'st_time_str': ss.st_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
                'end_time_str': ss.end_time.astimezone(pytz.timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M %p'),
            })

        scoutQuestionType = ScoutQuestionType.objects.all()

        return {'seasons': seasons, 'events': events, 'currentSeason': current_season, 'currentEvent': current_event,
                'users': users, 'userGroups': user_groups, 'phoneTypes': phone_types,
                'fieldSchedule': fieldSchedule, 'pitSchedule': pitSchedule, 'pastSchedule': pastSchedule,
                'scoutQuestionType': scoutQuestionType}

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init()
                serializer = ScoutAdminInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'GetScoutAdminInit', request.user.id,
                                   e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminInit', request.user.id)


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
                'date_st': datetime.datetime.strptime(e['start_date'], '%Y-%m-%d').astimezone(pytz.utc),
                'date_end': datetime.datetime.strptime(e['end_date'], '%Y-%m-%d').astimezone(pytz.utc),
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
        if has_access(request.user.id, auth_obj):
            try:
                req = self.sync_season(request.query_params.get('season_id', None))
                return ret_message(req)
            except Exception as e:
                return ret_message('An error occurred while syncing teams.', True, 'GetScoutAdminSyncSeason',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminSyncSeason', request.user.id)


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
        if has_access(request.user.id, auth_obj):
            try:
                req = self.set(request.query_params.get('season_id', None), request.query_params.get('event_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while setting the season.', True, 'GetScoutAdminSetSeason',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminSetSeason', request.user.id)


class GetScoutAdminAddSeason(APIView):
    """
    API endpoint to add a season
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def add(self, season):
        try:
            Season.objects.get(season=season)
            return ret_message('Season not added. Season ' + season + ' already exists.', True,
                               'GetScoutAdminAddSeason', self.request.user.id)
        except Exception as e:
            Season(season=season, current='n').save()

        return ret_message('Successfully added season: ' + season)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.add(request.query_params.get('season', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while setting the season.', True, 'GetScoutAdminAddSeason',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminAddSeason', request.user.id)


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

            sqs = ScoutQuestion.objects.filter(season=season)

            #QuestionOptions.objects.filter(sq__in=list(sqs.values_list('user_id', flat=True)))
            QuestionOptions.objects.filter(sq__in=sqs).delete()
            sqs.delete()

            e.delete()

        season.delete()

        return ret_message('Successfully deleted season: ' + season.season)

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.delete(request.query_params.get('season_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while deleting the season.', True, 'GetScoutAdminDeleteSeason',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminDeleteSeason', request.user.id)


class GetScoutAdminQuestionInit(APIView):
    """
    API endpoint to get the question init values for the scout admin screen
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_init(self, question_type):
        question_types = QuestionType.objects.filter(void_ind='n')

        try:
            current_season = Season.objects.get(current='y')
        except Exception as e:
            return ret_message('No season set, see an admin.', True, 'GetScoutAdminQuestionInit', self.request.user.id, e)

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
        if has_access(request.user.id, auth_obj):
            try:
                req = self.get_init(request.query_params.get('sq_typ', None))
                if type(req) == Response:
                    return req
                serializer = ScoutAdminQuestionInitSerializer(req)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, 'GetScoutAdminQuestionInit',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminQuestionInit', request.user.id)


class PostScoutAdminSaveScoutQuestion(APIView):
    """API endpoint to save new questions"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_question(self, data):
        try:
            try:
                current_season = Season.objects.get(current='y')
            except Exception as e:
                return ret_message('No season set, see an admin.', True, 'PostScoutAdminSaveQuestion',
                                   self.request.user.id, e)

            sq = ScoutQuestion(season=current_season, question_typ_id=data['question_typ'],  sq_typ_id=data['sq_typ'],
                               question=data['question'], order=data['order'], active='y', void_ind='n')

            sq.save()

            if data['sq_typ'] == 'field':
                questions_answered = ScoutField.objects.filter(void_ind='n')

                for qa in questions_answered:
                    ScoutFieldAnswer(scout_field=qa, sq=sq, answer='!EXIST', void_ind='n').save()
            elif data['sq_typ'] == 'pit':
                questions_answered = ScoutPit.objects.filter(void_ind='n')

                for qa in questions_answered:
                    ScoutPitAnswer(scout_pit=qa, sq=sq, answer='!EXIST', void_ind='n').save()




            for op in data['options']:
                QuestionOptions(option=op['option'], sq_id=sq.sq_id, active='y', void_ind='n').save()

            return ret_message('Saved question successfully.')
        except Exception as e:
            return ret_message('Couldn\'t save question', True, 'PostScoutAdminSaveQuestion', self.request.user.id, e)

    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'PostScoutAdminSaveScoutQuestion', request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_question(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the question.', True,
                                   'PostScoutAdminSaveScoutQuestion', request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutAdminSaveScoutQuestion', request.user.id)


class PostScoutAdminUpdateScoutQuestion(APIView):
    """API endpoint to update questions"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def update_question(self, data):
        sq = ScoutQuestion.objects.get(sq_id=data['sq_id'])

        sq.question = data['question']
        sq.order = data['order']
        sq.question_typ_id = data['question_typ']
        sq.save()

        for op in data['options']:
            if op.get('q_opt_id', None) is not None:
                o = QuestionOptions.objects.get(q_opt_id=op['q_opt_id'])
                o.option = op['option']
                o.active = op['active']
                o.save()
            else:
                QuestionOptions(option=op['option'], sq_id=sq.sq_id, active='y', void_ind='n').save()

        return ret_message('Question saved successfully')

    def post(self, request, format=None):
        serializer = ScoutQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'PostScoutAdminUpdateScoutQuestion', request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.update_question(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while updating the question.', True,
                                   'PostScoutAdminUpdateScoutQuestion', request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutAdminUpdateScoutQuestion', request.user.id)


class GetScoutAdminToggleScoutQuestion(APIView):
    """
    API endpoint to toggle a scout field question
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def toggle(self, sq_id):
        sq = ScoutQuestion.objects.get(sq_id=sq_id)

        if sq.active == 'n':
            sq.active = 'y'
        else:
            sq.active = 'n'

        sq.save()

        return ret_message('Successfully toggled the question state.')

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.toggle(request.query_params.get('sq_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the scout question.', True,
                                   'GetScoutAdminToggleScoutQuestion', request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminToggleScoutQuestion', request.user.id)


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

        return ret_message('Successfully toggled the option.')

    def get(self, request, format=None):
        if has_access(request.user.id, auth_obj):
            try:
                req = self.toggle(request.query_params.get('q_opt_id', None))
                return req
            except Exception as e:
                return ret_message('An error occurred while toggling the option.', True, 'GetScoutAdminToggleOption',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'GetScoutAdminToggleOption', request.user.id)


class PostScoutAdminSaveUser(APIView):
    """API endpoint to save user data"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_user(self, data):
        try:
            groups = []
            user = AuthUser.objects.get(username=data['user']['username'])
            user.first_name = data['user']['first_name']
            user.last_name = data['user']['last_name']
            user.phone = data['user']['phone']
            user.phone_type_id = data['user']['phone_type']
            user.save()

            for d in data['groups']:
                groups.append(d['name'])
                aug = AuthUserGroups.objects.filter(Q(group=AuthGroup.objects.get(name=d['name'])) & Q(user=user)).exists()
                if not aug:
                    AuthUserGroups(user=user, group=AuthGroup.objects.get(name=d['name'])).save()

            AuthUserGroups.objects.filter(~Q(group__in=AuthGroup.objects.filter(name__in=groups)) &
                                          Q(user=user)).delete()

            return ret_message('Saved user successfully')
        except Exception as e:
            return ret_message('Can\'t save the user', True, 'PostScoutAdminSaveUser', self.request.user.id, e)

    def post(self, request, format=None):
        serializer = ScoutAdminSaveUserSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'PostScoutAdminSaveUser', request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_user(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the user.', True, 'PostScoutAdminSaveUser',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutAdminSaveUser', request.user.id)


class PostScoutAdminSaveScoutScheduleEntry(APIView):
    """API endpoint to save scout schedule entry"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_scout_schedule(self, data):
        #local = pytz.timezone('US/Eastern')
        local = pytz.utc
        native = datetime.datetime.strptime(data['st_time'].replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S')
        local_dt = local.localize(native, is_dst=None)
        #st_utc_dt = local_dt.astimezone(pytz.utc)
        st_utc_dt = local_dt

        native = datetime.datetime.strptime(data['end_time'].replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S')
        local_dt = local.localize(native, is_dst=None)
        #end_utc_dt = local_dt.astimezone(pytz.utc)
        end_utc_dt = local_dt

        if st_utc_dt <= timezone.now():
            return ret_message('Start time can\'t be in the past.', True, 'PostScoutAdminSaveScoutScheduleEntry',
                               self.request.user.id)

        if end_utc_dt <= st_utc_dt:
            return ret_message('End time can\'t come before start.', True, 'PostScoutAdminSaveScoutScheduleEntry',
                               self.request.user.id)

        if data.get('scout_sch_id', None) is None:
            ScoutSchedule(user_id=data['user_id'], sq_typ_id=data['sq_typ'], st_time=st_utc_dt, end_time=end_utc_dt,
                          notified='n', void_ind='n').save()
            return ret_message('Saved schedule entry successfully')
        else:
            ss = ScoutSchedule.objects.get(scout_sch_id=data['scout_sch_id'])
            ss.user_id = data['user_id']
            ss.sq_typ_id = data['sq_typ']
            ss.st_time = st_utc_dt
            ss.end_time = end_utc_dt
            ss.notified = 'n'
            ss.void_ind = data['void_ind']
            ss.save()
            return ret_message('Updated schedule entry successfully')



    def post(self, request, format=None):
        serializer = ScoutScheduleSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'PostScoutAdminSaveScoutScheduleEntry', request.user.id,
                               serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_scout_schedule(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving the schedule entry.', True,
                                   'PostScoutAdminSaveScoutScheduleEntry', request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutAdminSaveScoutScheduleEntry', request.user.id)


class PostScoutAdminNotifyUser(APIView):
    """API endpoint to notify users"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def notify_user(self, data):
        for d in data:
            if d.get('notify', 'n') == 'y':
                user = AuthUser.objects.get(id=d['user_id'])
                ss = ScoutSchedule.objects.get(scout_sch_id=d['scout_sch_id'])
                st_time = ss.st_time
                st_time = st_time.astimezone(pytz.timezone('US/Eastern'))
                st_time = st_time.strftime('%m/%d/%Y %I:%M %p')

                end_time = ss.end_time
                end_time = end_time.astimezone(pytz.timezone('US/Eastern'))
                end_time = end_time.strftime('%m/%d/%Y %I:%M %p')

                data = {
                    'scout_location': d['sq_typ'],
                    'scout_time_st': st_time,
                    'scout_time_end': end_time,
                    'lead_scout': self.request.user.first_name + ' ' + self.request.user.last_name
                }
                send_email.send_message(user.phone + user.phone_type.phone_type, 'Time to Scout!', 'notify_scout',
                                        data)

                scout_sch = ScoutSchedule.objects.get(scout_sch_id=d['scout_sch_id'])
                scout_sch.notified = 'y'
                scout_sch.save()

        return ret_message('Successfully notified selected users')

    def post(self, request, format=None):
        serializer = ScoutScheduleSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'PostScoutAdminNotifyUser', request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.notify_user(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while notifying user.', True, 'PostScoutAdminNotifyUser',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutAdminNotifyUser', request.user.id)


class PostScoutAdminSavePhoneType(APIView):
    """API endpoint to save phone types"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def save_phone_type(self, data):

        if data.get('phone_type_id', None) is not None:
            pt = PhoneType.objects.get(phone_type_id=data['phone_type_id'])
            pt.phone_type = data['phone_type']
            pt.carrier = data['carrier']
            pt.save()
        else:
            PhoneType(phone_type=data['phone_type'], carrier=data['carrier']).save()

        return ret_message('Successfully saved phone type.')

    def post(self, request, format=None):
        serializer = PhoneTypeSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, 'PostScoutAdminAddPhoneType', request.user.id, serializer.errors)

        if has_access(request.user.id, auth_obj):
            try:
                req = self.save_phone_type(serializer.data)
                return req
            except Exception as e:
                return ret_message('An error occurred while saving phone type.', True, 'PostScoutAdminAddPhoneType',
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, 'PostScoutAdminAddPhoneType', request.user.id)
