from rest_framework import serializers

from user.serializers import PermissionSerializer


class AlertTypeSerializer(serializers.Serializer):
    alert_typ = serializers.CharField(max_length=50)
    alert_typ_nm = serializers.CharField(max_length=255)
    subject = serializers.CharField(max_length=255, allow_null=True)
    body = serializers.CharField(max_length=4000, allow_null=True)
    last_run = serializers.DateTimeField(allow_null=True)
    permission = PermissionSerializer(allow_null=True, required=False)
    void_ind = serializers.CharField(max_length=1, default="n")