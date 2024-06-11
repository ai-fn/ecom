from typing import Any
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from api.mixins import SerializerGetPricesMixin
from api.serializers import (
    CategorySerializer,
    CharacteristicValueSerializer,
    ProductImageSerializer,
)
from api.serializers import BrandSerializer
from shop.models import Brand, Category, Product, ProductFile


class ProductDetailSerializer(SerializerGetPricesMixin, serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
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
        ]

    def get_files(self, obj) -> ReturnList | Any | ReturnDict:
        return ProductFileSerializer(obj.files, many=True).data


class ProductFileSerializer(serializers.ModelSerializer):
    
    file = serializers.SerializerMethodField()

    class Meta:
        model = ProductFile
        exclude = [
            "created_at",
            "updated_at",
        ]

    def get_file(self, obj) -> str | None:
        return obj.file.url if obj.file else None
