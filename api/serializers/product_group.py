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

    products = SerializerMethodField()
    characteristic = SerializerMethodField()

    class Meta:
        model = ProductGroup
        exclude = ["updated_at", "created_at"]

    def get_products(self, obj) -> Any:
        context = {"characteristic_name": obj.characteristic.name, **self.context}
        if self.context.get("visual_groups"):
            return ProductForGroupImageSerializer(
                obj.products.all(), many=True, context=context
            ).data

        return ProductForGroupNonImageSerializer(
            obj.products.all(), many=True, context=context
        ).data

    def get_characteristic(self, obj) -> str:
        return obj.characteristic.name if obj.characteristic else None
