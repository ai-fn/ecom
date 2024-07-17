from loguru import logger
from api.serializers import ActiveModelSerializer
from rest_framework import serializers
from shop.models import CharacteristicValue, Product


class CharacteristicValueSerializer(ActiveModelSerializer):
    characteristic_name = serializers.CharField(
        source="characteristic.name", read_only=True
    )
    characteristic_id = serializers.PrimaryKeyRelatedField(
        queryset=CharacteristicValue.objects.all(), source="characteristic"
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product"
    )

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

    def update(self, instance: CharacteristicValue, validated_data):
        product_id = getattr(validated_data.pop("product", None), "id", None)
        if product_id and instance.product.id != product_id:
            instance, created = self.Meta.model.objects.get_or_create(
                product__id=product_id,
                characteristic=instance.characteristic,
                defaults={"slug": instance.slug},
            )
            if created:
                logger.info(
                    f"Created new CharacteristiValue for product with pk {product_id}: {instance}"
                )

        return super().update(instance, validated_data)
