from rest_framework import serializers

from account.models import City
from shop.models import Category, Product, Promo
from api.serializers import CategoryDetailSerializer, CitySerializer, ProductCatalogSerializer


class PromoSerializer(serializers.ModelSerializer):
    products = ProductCatalogSerializer(many=True, read_only=True)
    products_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    categories = CategoryDetailSerializer(many=True, read_only=True)
    categories_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=False,
        source="category",
        queryset=Category.objects.all(),
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
            "categories",
            "categories_id",
            "products",
            "products_id",
            "image",
            "cities",
            "cities_id",
            "active_to",
            "is_active",
            "thumb_img",
        ]

    def create(self, validated_data):
        products_data = validated_data.pop("products_id", [])
        promo = super().create(validated_data)
        promo.products.set(products_data)
        return promo

    def update(self, instance, validated_data):
        products_data = validated_data.pop("products_id", [])
        instance = super().update(instance, validated_data)
        instance.products.set(products_data)
        return instance
