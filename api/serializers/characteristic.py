from rest_framework import serializers

from shop.models import Characteristic


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = [
            "id",
            "name",
            "category",
        ]
