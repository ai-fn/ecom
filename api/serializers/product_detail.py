from typing import Any
from api.serializers import ActiveModelSerializer
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from api.mixins import SerializerGetPricesMixin
from api.serializers import (
    CategorySerializer,
    CharacteristicValueSerializer,
    ProductImageSerializer,
)
from api.serializers import (
    BrandSerializer,
    ProductGroupSerializer,
)
from shop.models import Brand, Category, Product, ProductFile, ProductGroup
from rest_framework import serializers


class ProductDetailSerializer(SerializerGetPricesMixin, ActiveModelSerializer):
    images = ProductImageSerializer(many=True)
    city_price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    characteristic_values = CharacteristicValueSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source="category"
    )
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        write_only=True,
        source="brand",
    )
    files = serializers.SerializerMethodField()
    priority = serializers.IntegerField(read_only=True)
    groups = serializers.SerializerMethodField()

    def create(self, validated_data):
        images_data: list[dict] = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        
        for image_data in images_data:
            product_id = image_data.pop("product", product.pk)
            image_data["product_id"] = product_id
            serializer = ProductImageSerializer(data=image_data)
            serializer.is_valid(raise_exception=1)
            serializer.save()
        
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                product = image_data.pop("product", instance)
                image_data["product_id"] = product.pk
                serializer = ProductImageSerializer(data={**image_data})
                serializer.is_valid(raise_exception=1)
                serializer.save()
        
        return super().update(instance, validated_data)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_id",
            "title",
            "brand",
            "article",
            "brand_id",
            "description",
            "slug",
            "created_at",
            "city_price",
            "old_price",
            "characteristic_values",
            "images",
            "in_stock",
            "is_popular",
            "priority",
            "thumb_img",
            "files",
            "groups",
        ]
    
    def get_groups(self, obj) -> None | ReturnDict:
        context = {"current_product": obj.id}
        groups = ProductGroup.objects.filter(products=obj)
        visual_groups = groups.filter(characteristic__name__iexact="цвет")
        return {
            "visual_groups": ProductGroupSerializer(
                visual_groups, many=True, context={"visual_groups": True, **context}
            ).data,
            "non_visual_group": ProductGroupSerializer(
                groups.exclude(id__in=visual_groups), many=True, context=context
            ).data,
        }

    def get_files(self, obj) -> ReturnList | Any | ReturnDict:
        return ProductFileSerializer(obj.files, many=True).data


class ProductFileSerializer(ActiveModelSerializer):

    file = serializers.SerializerMethodField()

    class Meta:
        model = ProductFile
        exclude = [
            "created_at",
            "updated_at",
        ]

    def get_file(self, obj) -> str | None:
        return obj.file.url if obj.file else None
