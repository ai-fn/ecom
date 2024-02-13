from rest_framework import serializers

from api.serializers import ProductImageSerializer
from shop.models import Product


class ProductCatalogSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )
    city_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        read_only=True,
    )
    old_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "brand",
            "image",
            "slug",
            "city_price",
            "old_price",
            "images",
        ]
