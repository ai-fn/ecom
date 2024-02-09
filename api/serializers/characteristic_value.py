from rest_framework import serializers

from shop.models import CharacteristicValue


class CharacteristicValueSerializer(serializers.ModelSerializer):
    characteristic_name = serializers.CharField(source="characteristic.name")

    class Meta:
        model = CharacteristicValue
        fields = [
            "id",
            "characteristic_name",
            "value",
        ]