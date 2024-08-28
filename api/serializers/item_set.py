from typing import OrderedDict
from rest_framework import serializers 
from api.serializers.product_catalog import ProductCatalogSerializer
from shop.models import ItemSet, ItemSetElement, Product


class ItemSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemSet
        fields = [
            "id",
            "title",
            "description",
            "itemset_type",
            "order",
            "elements",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['elements'] = ItemSetElementSerializer(instance.elements.all(), many=True).data
        return data


class ItemSetElementSerializer(serializers.ModelSerializer):

    content_object = serializers.SerializerMethodField()

    class Meta:
        model = ItemSetElement
        fields = [
            "id",
            "item_set",
            "order",
            "content_type",
            "object_id",
            "content_object",
        ]
        extra_kwargs = {
            "content_type": {"write_only": True},
            "object_id": {"write_only": True},
        }

    def get_content_object(self, obj) -> OrderedDict | None:
        if isinstance(obj.content_object, Product):
            return ProductCatalogSerializer(obj.content_object).data
