from loguru import logger
from api.serializers import ActiveModelSerializer
from rest_framework import serializers
from shop.models import Characteristic, CharacteristicValue, Product


class CharacteristicValueSerializer(ActiveModelSerializer):
    characteristic_name = serializers.CharField(
        source="characteristic.name", read_only=True
    )
    characteristic_id = serializers.PrimaryKeyRelatedField(
        queryset=Characteristic.objects.all(), source="characteristic"
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product"
    )
    slug = serializers.SlugField(required=False)

    class Meta:
        model = CharacteristicValue
        fields = [
            "id",
            "characteristic_name",
            "characteristic_id",
            "product_id",
            "value",
            "slug",
        ]
        unique_together = ["product_id", "characteristic_id"]

    def validate(self, data):
        product_id = data.get('product_id')
        characteristic_id = data.get('characteristic_id')

        if (instance := CharacteristicValue.objects.filter(product_id=product_id, characteristic_id=characteristic_id).first()):
            data['instance'] = instance

        return data


class SimplifiedCharacteristicValueSerializer(serializers.Serializer):
    characteristic_id = serializers.PrimaryKeyRelatedField(queryset=Characteristic.objects.all())
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    value = serializers.CharField()
