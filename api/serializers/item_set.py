from typing import OrderedDict
from rest_framework import serializers 
from api.serializers import (
    BannerSerializer,
    PromoSerializer,
    ProductCatalogSerializer,
    CategorySerializer,
    SliderSerializer,
)
from shop.models import (
    Banner,
    Category,
    ItemSet,
    ItemSetElement,
    Product,
    Promo,
    Slider,
)


class ItemSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ItemSet
        fields = [
            "id",
            "title",
            "description",
            "itemset_type",
            "grid_type",
            "order",
            "elements",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['elements'] = ItemSetElementSerializer(instance.elements.all(), context=self.context, many=True).data
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

            serializer_class = ProductCatalogSerializer
        elif isinstance(obj.content_object, Banner):
            serializer_class = BannerSerializer

        elif isinstance(obj.content_object, Category):
            serializer_class = CategorySerializer

        elif isinstance(obj.content_object, Promo):
            serializer_class = PromoSerializer

        elif isinstance(obj.content_object, Slider):
            serializer_class = SliderSerializer

        return serializer_class(context=self.context, instance=obj.content_object).data
