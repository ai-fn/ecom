from rest_framework import serializers

from shop.models import CharacteristicValue


class CharacteristicValueSerializer(serializers.ModelSerializer):
    characteristic_name = serializers.CharField(source="characteristic.name", read_only=True)
    characteristic_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CharacteristicValue
        fields = [
            "id",
            "characteristic_name",
            "characteristic_id",
            "product_id",
            "value",
        ]