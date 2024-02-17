from django.db import transaction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import alerts.util
import form.util
import user.util
from form.models import Question, QuestionAnswer, FormType
from form.serializers import QuestionSerializer, SaveResponseSerializer, SaveScoutSerializer, \
    QuestionInitializationSerializer, ResponseSerializer, QuestionAggregateSerializer, QuestionAggregateTypeSerializer
from general.security import has_access, ret_message
from scouting.models import Event, Season, ScoutField, ScoutPit

app_url = 'form/'


class GetQuestions(APIView):
    """
    API endpoint to init form editor
    """
    endpoint = 'get-questions/'

    def get(self, request, format=None):
        try:
            questions = form.util.get_questions(request.query_params['form_typ'])
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting questions.', True, app_url + self.endpoint,
                               request.user.id, e)


class GetFormInit(APIView):
    """
    API endpoint to init form editor
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'form-init/'

    def get(self, request, format=None):
        if has_access(request.user.id, 'admin') or has_access(request.user.id, 'scoutadmin'):
            try:
                questions = form.util.get_questions(request.query_params['form_typ'])
                question_types = form.util.get_question_types()
                form_sub_types = form.util.get_form_sub_types(request.query_params['form_typ'])
                serializer = QuestionInitializationSerializer({
                    "questions": questions,
                    "question_types": question_types,
                    "form_sub_types": form_sub_types,
                })
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while initializing.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SaveQuestion(APIView):
    """API endpoint to save new questions"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-question/'

    def post(self, request, format=None):
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id,
                               serializer.errors)

        if has_access(request.user.id, 'admin') or has_access(request.user.id, 'scoutadmin'):
            try:
                with transaction.atomic():
                    form.util.save_question(serializer.validated_data)
                return ret_message('Saved question successfully.')
            except Exception as e:
                return ret_message('An error occurred while saving the question.', True,
                                   app_url + self.endpoint, request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class SaveAnswers(APIView):
    """
    API endpoint to save answers
    """
    # authentication_classes = (JWTAuthentication,)
    # permission_classes = (IsAuthenticated,)
    endpoint = 'save-answers/'

    def post(self, request, format=None):
        success_msg = 'Response saved successfully'
        form_typ = request.data.get('form_typ', '')
        with transaction.atomic():
            try:
                if form_typ in ['field', 'pit']:
                    # field and pit responses must be authenticated
                    if (form_typ == 'field' and has_access(request.user.id, 'scoutfield')) or (
                            form_typ == 'pit' and has_access(request.user.id, 'scoutpit')):
                        try:
                            current_event = Event.objects.get(
                                Q(season=Season.objects.get(current='y')) & Q(current='y'))
                        except Exception as e:
                            raise Exception('No event set, see an admin')

                        # Try to deserialize as a field or pit answer
                        serializer = SaveScoutSerializer(data=request.data)
                        if serializer.is_valid():
                            form_type = FormType.objects.get(form_typ=serializer.data['form_typ'])
                            r = form.models.Response(form_typ=form_type)
                            r.save()

                            if serializer.data['form_typ'] == 'field':
                                sf = ScoutField(
                                    event=current_event, team_no_id=serializer.data['team'],
                                    match_id=serializer.data.get('match', None),
                                    user_id=self.request.user.id, response_id=r.response_id, void_ind='n')
                                sf.save()

                                for d in serializer.data.get('question_answers', []):
                                    form.util.save_question_answer(d['answer'],
                                                                   Question.objects.get(question_id=d['question_id']),
                                                                   r)
                            else:
                                try:
                                    sp = ScoutPit.objects.get(Q(team_no_id=serializer.data['team']) & Q(void_ind='n') &
                                                              Q(event=current_event))
                                except Exception as e:
                                    sp = ScoutPit(event=current_event, team_no_id=serializer.data['team'],
                                                  user_id=self.request.user.id, response_id=r.response_id, void_ind='n')
                                    sp.save()

                                for d in serializer.data.get('question_answers', []):
                                    try:
                                        spa = QuestionAnswer.objects.get(
                                            Q(response_id=sp.response_id) & Q(question_id=d['question_id']) &
                                            Q(void_ind='n'))
                                        spa.answer = d.get('answer', '')
                                        spa.save()
                                    except Exception as e:
                                        form.util.save_question_answer(d.get('answer', ''),
                                                                       Question.objects.get(
                                                                           question_id=d['question_id']),
                                                                       r)
                            return ret_message(success_msg)
                        raise Exception('Invalid Data')
                    else:
                        return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)
                else:
                    # regular response
                    serializer = SaveResponseSerializer(data=request.data)
                    if serializer.is_valid():
                        form_type = FormType.objects.get(form_typ=serializer.data['form_typ'])
                        r = form.models.Response(form_typ=form_type)
                        r.save()

                        for d in serializer.data.get('question_answers', []):
                            form.util.save_question_answer(d['answer'],
                                                           Question.objects.get(question_id=d['question_id']),
                                                           response=r)

                        alert = []
                        users = user.util.get_users_with_permission('site_forms_notif')
                        for u in users:
                            alert.append(
                                alerts.util.stage_alert(u, form_type.form_nm, 'A new response has been logged.'))
                        for a in alert:
                            for acct in ['email', 'message', 'notification']:
                                alerts.util.stage_alert_channel_send(a, acct)
                        return ret_message(success_msg)
                    raise Exception('Invalid Data')
            except Exception as e:
                return ret_message('An error occurred while saving answers.', True, app_url + self.endpoint,
                                   request.user.id, e)


class GetResponse(APIView):
    """
    API endpoint to get a form response
    """
    endpoint = 'get-response/'

    def get(self, request, format=None):
        if has_access(request.user.id, 'admin'):
            try:
                response = form.util.get_response(request.query_params['response_id'])
                serializer = QuestionSerializer(response, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while getting responses.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class GetResponses(APIView):
    """
    API endpoint to get a form responses
    """
    endpoint = 'get-responses/'

    def get(self, request, format=None):
        if has_access(request.user.id, 'admin'):
            try:
                responses = form.util.get_responses(request.query_params['form_typ'])
                serializer = ResponseSerializer(responses, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while getting responses.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class QuestionAggregateView(APIView):
    """
    API endpoint to manage the question aggregate groups
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'question-aggregate/'

    def get(self, request, format=None):
        if has_access(request.user.id, 'admin') or has_access(request.user.id, 'scoutadmin'):
            try:
                qas = form.util.get_question_aggregates(request.query_params['form_typ'])
                serializer = QuestionAggregateSerializer(qas, many=True)
                return Response(serializer.data)
            except Exception as e:
                return ret_message('An error occurred while getting question aggregates.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)

    def post(self, request, format=None):
        serializer = QuestionAggregateSerializer(data=request.data)
        if not serializer.is_valid():
            return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, serializer.errors)

        if has_access(request.user.id, 'admin') or has_access(request.user.id, 'scoutadmin'):
            try:
                with transaction.atomic():
                    form.util.save_question_aggregate(serializer.validated_data)
                return ret_message('Saved question aggregate successfully')
            except Exception as e:
                return ret_message('An error occurred while saving the question aggregate.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)


class QuestionAggregateTypeView(APIView):
    """
    API endpoint to manage the question aggregate types
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'question-aggregate-types/'

    def get(self, request, format=None):
        try:
            qas = form.util.get_question_aggregate_types()
            serializer = QuestionAggregateTypeSerializer(qas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return ret_message('An error occurred while getting question aggregate types.', True, app_url + self.endpoint,
                               request.user.id, e)