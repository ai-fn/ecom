from rest_framework import serializers

from api.serializers.category import CategorySerializer
from api.serializers import CitySerializer
from api.serializers.product_detail import ProductDetailSerializer
from shop.models import Promo


class PromoSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()
    category = CategorySerializer()
    cities = CitySerializer(many=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Promo
        fields = [
            "id",
            "name",
            "category",
            "product",
            "image",
            "cities",
            "active_to",
            "is_active",
        ]
