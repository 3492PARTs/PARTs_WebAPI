from rest_framework import serializers


class TeamSerializer(serializers.Serializer):
    team_no = serializers.IntegerField()
    team_nm = serializers.CharField()

    checked = serializers.BooleanField(required=False)
    pit_result = serializers.IntegerField()
