from typing import OrderedDict
from rest_framework import serializers 
from api.serializers import (
    BannerSerializer,
    PromoSerializer,
    ProductCatalogSerializer,
    CategorySliderSerializer,
    SliderSerializer,
    BrandSerializer,
)
from api.mixins import PriceFilterMixin
from shop.models import (
    ItemSet,
    ItemSetElement,
)


class ItemSetSerializer(serializers.ModelSerializer, PriceFilterMixin):

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

    def to_representation(self, instance: ItemSet):
        data = super().to_representation(instance)
        elems = instance.elements.all()
        if instance.itemset_type == ItemSet.ItemSetType.PRODUCT:
            elems = self.get_products_only_with_price(elems, domain=self.context.get("city_domain", ""), prefix="products__")

        data['elements'] = ItemSetElementSerializer(elems, context=self.context, many=True).data
        return data


class ItemSetElementSerializer(serializers.ModelSerializer):

    content_object = serializers.SerializerMethodField()
    ALLOWED_MODELS = {
        "product": ProductCatalogSerializer,
        "brand": BrandSerializer,
        "category": CategorySliderSerializer,
        "banner": BannerSerializer,
        "slider": SliderSerializer,
        "promo": PromoSerializer,
    }

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
        obj_cls_name = obj.content_object.__class__.__name__.lower()
        serializer_class = self.ALLOWED_MODELS.get(obj_cls_name)
        if serializer_class is None:
            return serializer_class

        return serializer_class(context=self.context, instance=obj.content_object).data
