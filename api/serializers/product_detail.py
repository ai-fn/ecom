from typing import Any
from loguru import logger

from django.db import transaction

from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework import serializers

from api.serializers import ActiveModelSerializer
from api.mixins import (
    RatingMixin,
    SerializerGetPricesMixin, 
)
from api.serializers import (
    CategorySerializer,
    CharacteristicValueSerializer,
    SimplifiedCharacteristicValueSerializer,
    ProductImageSerializer,
)
from api.serializers import (
    BrandSerializer,
    ProductGroupSerializer,
)
from shop.models import CharacteristicValue, Product, ProductFile, ProductGroup


class ProductDetailSerializer(RatingMixin, SerializerGetPricesMixin, ActiveModelSerializer):
    images = ProductImageSerializer(many=True)
    city_price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    priority = serializers.IntegerField(read_only=True)
    characteristic_values = SimplifiedCharacteristicValueSerializer(many=True, write_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "h1_tag",
            "category",
            "title",
            "brand",
            "article",
            "description",
            "slug",
            "created_at",
            "city_price",
            "old_price",
            "characteristic_values",
            "images",
            "in_stock",
            "is_popular",
            "is_new",
            "priority",
            "thumb_img",
            "files",
            "groups",
            "rating",
            "unit",
            "package_weight",
            "package_length",
            "package_width",
            "package_height",
        ]

    def create(self, validated_data):
        images_data: list[dict] = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)
        
        characteristic_values = validated_data.pop("characteristic_values", [])
        with transaction.atomic():
            for char_val in characteristic_values:
                serializer = CharacteristicValueSerializer(data=char_val)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        with transaction.atomic():
            for image_data in images_data:
                product_id = image_data.pop("product", product.pk)
                image_data["product_id"] = product_id
                serializer = ProductImageSerializer(data=image_data)
                serializer.is_valid(raise_exception=1)
                serializer.save()

        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", [])
        characteristic_values = validated_data.pop("characteristic_values", [])

        if images_data:
            instance.images.all().delete()
            with transaction.atomic():
                for image_data in images_data:
                    product = image_data.pop("product", instance)
                    image_data["product_id"] = product.pk
                    serializer = ProductImageSerializer(data={**image_data})
                    serializer.is_valid(raise_exception=1)
                    serializer.save()

        with transaction.atomic():
            for char_val in characteristic_values:

                CharacteristicValue.objects.update_or_create(
                    characteristic=char_val["characteristic_id"],
                    product=char_val["product_id"],
                    defaults={"value": char_val["value"]},
                )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.brand:
            data["brand"] = BrandSerializer(instance.brand).data
        if instance.category:
            data["category"] = CategorySerializer(instance.category).data
        
        if instance.characteristic_values.exists():
            data["characteristic_values"] = CharacteristicValueSerializer(instance.characteristic_values.all(), many=True).data

        return data

    def get_groups(self, obj) -> None | ReturnDict:
        context = {"current_product": obj.id}
        visual_groups = obj.groups.filter(characteristic__name__istartswith="цвет")
        return {
            "visual_groups": ProductGroupSerializer(
                visual_groups, many=True, context={"visual_groups": True, **context}
            ).data,
            "non_visual_group": ProductGroupSerializer(
                obj.groups.exclude(id__in=visual_groups), many=True, context=context
            ).data,
        }

    def get_files(self, obj) -> ReturnList | Any | ReturnDict:
        return ProductFileSerializer(obj.files, many=True).data


class ProductFileSerializer(ActiveModelSerializer):

    class Meta:
        model = ProductFile
        exclude = [
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["file"] = instance.file.url if instance.file else None
        return data
