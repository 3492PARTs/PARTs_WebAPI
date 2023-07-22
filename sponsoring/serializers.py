from rest_framework import serializers


class ItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=False)
    item_nm = serializers.CharField()
    item_desc = serializers.CharField()
    quantity = serializers.IntegerField
    item_desc = serializers.CharField()


class SponsorSerializer(serializers.Serializer):
    sponsor_id = serializers.IntegerField(required=False)
    sponsor_nm = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()


class ItemSponsorSerializer(serializers.Serializer):
    item_sponsor_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField
    sponsor_id = serializers.IntegerField
    quantity = serializers.IntegerField
