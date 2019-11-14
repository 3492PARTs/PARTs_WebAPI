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


class GetScoutFieldInputs(APIView):
    """
    API endpoint to get links a user has based on permissions
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_questions(self):
        questions = ScoutFieldQuestion.objects.filter(Q(season=2) & Q(void_ind='n')).order_by('order')

        return questions

    def get(self, request, format=None):
        if has_access(request.user.id, 1):
            req = self.get_questions()
            serializer = QuestionSerializer(req, many=True)
            return Response(serializer.data)
        else:
            return ret_message('You do not have access', True)
