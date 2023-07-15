from django.db import transaction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import form.util
from form.models import Question, QuestionAnswer
from form.serializers import QuestionSerializer, SaveResponseSerializer, SaveScoutSerializer, \
    QuestionInitializationSerializer
from general.security import has_access, ret_message
from scouting.models import Event, Season, ScoutField, ScoutPit

auth_obj = 50
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
        if has_access(request.user.id, auth_obj):
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

        if has_access(request.user.id, auth_obj):
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
    API endpoint to save scout field answers
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    endpoint = 'save-answers/'

    def post(self, request, format=None):
        success_msg = 'Response saved successfully'
        if has_access(request.user.id, auth_obj):
            try:
                try:
                    current_event = Event.objects.get(
                        Q(season=Season.objects.get(current='y')) & Q(current='y'))
                except Exception as e:
                    raise Exception('No event set, see an admin')

                serializer = SaveScoutSerializer(data=request.data)
                if serializer.is_valid():
                    with transaction.atomic():
                        if (serializer.data['form_typ'] == 'field'):
                            sf = ScoutField(
                                event=current_event, team_no_id=serializer.data['team'],
                                match_id=serializer.data.get('match', None),
                                user_id=self.request.user.id, void_ind='n')
                            sf.save()

                            for d in serializer.data.get('question_answers', []):
                                form.util.save_question_answer(d['answer'], Question.objects.get(question_id=d['question_id']),
                                                               scout_field=sf)
                        else:
                            try:
                                sp = ScoutPit.objects.get(Q(team_no_id=serializer.data['team']) & Q(void_ind='n') &
                                                          Q(event=current_event))
                            except Exception as e:
                                sp = ScoutPit(event=current_event, team_no_id=serializer.data['team'],
                                              user_id=self.request.user.id, void_ind='n')
                                sp.save()

                            for d in serializer.data.get('question_answers', []):
                                try:
                                    spa = QuestionAnswer.objects.get(Q(scout_pit=sp) & Q(question_id=d['question_id']) &
                                                                     Q(void_ind='n'))
                                    spa.answer = d.get('answer', '')
                                except Exception as e:
                                    form.util.save_question_answer(d.get('answer', ''),
                                                                   Question.objects.get(question_id=d['question_id']),
                                                                   scout_pit=sp)
                        return ret_message(success_msg)

                serializer = SaveResponseSerializer(data=request.data)
                if serializer.is_valid():
                    with transaction.atomic():
                        r = form.models.Response(form_typ_id=serializer.data['form_typ'])
                        r.save()

                        for d in serializer.data.get('question_answers', []):
                            form.util.save_question_answer(d['answer'], Question.objects.get(question_id=d['question_id']),
                                                           response=r)
                        return ret_message(success_msg)

                return ret_message('Invalid data', True, app_url + self.endpoint, request.user.id, serializer.errors)
            except Exception as e:
                return ret_message('An error occurred while saving answers.', True, app_url + self.endpoint,
                                   request.user.id, e)
        else:
            return ret_message('You do not have access.', True, app_url + self.endpoint, request.user.id)



