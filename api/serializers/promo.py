from rest_framework import serializers

from account.models import City
from api.serializers.category import CategorySerializer
from api.serializers import CitySerializer
from api.serializers.product_detail import ProductDetailSerializer
from shop.models import Category, Product, Promo


class PromoSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="product", queryset=Product.objects.all()
    )
    category = CategorySerializer()
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="category", queryset=Category.objects.all()
    )
    cities = CitySerializer(many=True, read_only=True)
    cities_id = serializers.PrimaryKeyRelatedField(
        many=True, queryset=City.objects.all(), write_only=True
    )
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Promo
        fields = [
            "id",
            "name",
            "category",
            "category_id",
            "product",
            "product_id",
            "image",
            "cities",
            "cities_id",
            "active_to",
            "is_active",
        ]
