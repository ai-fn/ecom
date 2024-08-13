from typing import Any
from api.serializers import ActiveModelSerializer

from django.db.models import QuerySet
from shop.models import CharacteristicValue, Product, ProductGroup
from rest_framework.serializers import SerializerMethodField


class ProductForGroupNonImageSerializer(ActiveModelSerializer):
    characteristics = SerializerMethodField()
    is_selected = SerializerMethodField()
    category_slug = SerializerMethodField()

    def get_category_slug(self, obj) -> str:
        return obj.category.slug

    def get_is_selected(self, obj) -> bool:
        return self.context.get("current_product") == obj.id

    def get_characteristics(self, obj) -> QuerySet:
        characteristic_values = CharacteristicValue.objects.filter(product=obj)
        if name := self.context.get("characteristic_name"):
            characteristic_values = characteristic_values.filter(
                characteristic__name=name
            )

        return characteristic_values.values("id", "value", "characteristic__name")

    class Meta:
        model = Product
        fields = ["id", "title", "slug", "category_slug", "characteristics", "is_selected"]


class ProductForGroupImageSerializer(ProductForGroupNonImageSerializer):

    catalog_image = SerializerMethodField()

    def get_catalog_image(self, obj) -> str:
        return obj.catalog_image.url if obj.catalog_image else None
    
    class Meta(ProductForGroupNonImageSerializer.Meta):
        fields = ProductForGroupNonImageSerializer.Meta.fields + ["catalog_image"]


class ProductGroupSerializer(ActiveModelSerializer):

    class Meta:
        model = ProductGroup
        exclude = ["updated_at", "created_at"]


    def to_representation(self, instance):
        data = super().to_representation(instance)

        context = {"characteristic_name": instance.characteristic.name, **self.context}
        if self.context.get("visual_groups"):
            products = ProductForGroupImageSerializer(
                instance.products.all(), many=True, context=context
            ).data
        else:
            products = ProductForGroupNonImageSerializer(
                instance.products.all(), many=True, context=context
            ).data

        data['products'] = products
        data['characteristic'] = instance.characteristic.name if instance.characteristic else None
        return data
