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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["content_type"] = instance.content_type.model
        return data
    
    def get_content_object(self, obj):
        if isinstance(obj.content_object, Product):
            return ProductCatalogSerializer(obj.content_object).data
