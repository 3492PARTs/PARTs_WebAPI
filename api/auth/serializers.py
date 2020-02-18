from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'phone_type')
        extra_kwargs = {
            'username': {
                'validators': [],
            }
        }


class AuthGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthGroup
        fields = '__all__'


class UserLinksSerializer(serializers.Serializer):
    MenuName = serializers.CharField()
    RouterLink = serializers.CharField()


class PhoneTypeSerializer(serializers.Serializer):
    phone_type_id = serializers.IntegerField(required=False)
    carrier = serializers.CharField()
    phone_type = serializers.CharField()

    
class RetMessageSerializer(serializers.Serializer):
    retMessage = serializers.CharField()
    error = serializers.BooleanField()
    
class ErrorSerializer(serializers.Serializer):
    error_log_id = serializers.IntegerField()
    user = UserSerializer(required=False)
    location = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    exception = serializers.CharField(required=False)
    time = serializers.DateTimeField()
    void_ind = serializers.CharField()

    
class PaginatedErrorSerializer(pagination.PaginationSerializer):
    """
    TODO Serializes page objects of user querysets.
    """
    class Meta:
        object_serializer_class = ErrorSerializer
        
