from rest_framework import serializers

from api.mixins import SerializerGetPricesMixin
from api.serializers import (
    CategorySerializer,
    CharacteristicValueSerializer,
    ProductImageSerializer,
)
from api.serializers import BrandSerializer
from shop.models import Brand, Category, Product


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
    priority = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_id",
            "title",
            "brand",
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
        ]
