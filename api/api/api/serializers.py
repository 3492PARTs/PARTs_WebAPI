from rest_framework import serializers
from .models import *


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutFieldQuestion
        fields = '__all__'
