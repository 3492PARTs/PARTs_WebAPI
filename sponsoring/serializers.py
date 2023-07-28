from rest_framework import serializers


class SaveItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=False)
    item_nm = serializers.CharField()
    item_desc = serializers.CharField()
    quantity = serializers.IntegerField()
    active = serializers.CharField()
    img = serializers.FileField(required=False)


class ItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=False)
    item_nm = serializers.CharField()
    item_desc = serializers.CharField()
    quantity = serializers.IntegerField()
    sponsor_quantity = serializers.IntegerField(required=False)
    active = serializers.CharField()
    img_url = serializers.CharField()


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


class SaveSponsorOrderSerializer(serializers.Serializer):
    items = ItemSerializer(many=True)
    sponsor = SponsorSerializer()
