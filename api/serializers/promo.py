from rest_framework import serializers
from shop.models import Promo
from api.mixins import AnnotateProductMixin, PriceFilterMixin
from api.serializers import (
    ActiveModelSerializer,
    CategoryDetailSerializer,
    CitySerializer,
    ProductCatalogSerializer,
)


class PromoSerializer(ActiveModelSerializer, PriceFilterMixin, AnnotateProductMixin):
    products = ProductCatalogSerializer(many=True, read_only=True)
    categories = CategoryDetailSerializer(many=True, read_only=True)
    cities = CitySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Promo
        fields = [
            "id",
            "name",
            "categories",
            "products",
            "image",
            "cities",
            "active_to",
            "is_active",
            "thumb_img",
        ]
    
    def to_representation(self, instance):
        self.request = getattr(self.context.get("view"), "request", None)
        data = super().to_representation(instance)

        products = self.annotate_queryset(
            self.get_products_only_with_price(
                instance.products.all(), self.context.get("city_domain", "")
            )
        )

        data["cities"] = CitySerializer(instance.cities.all(), many=True).data
        data["categories"] = CategoryDetailSerializer(
            instance.categories.all(), many=True
        ).data
        data["products"] = ProductCatalogSerializer(products, many=True).data
        return data

    def create(self, validated_data):
        products_data = validated_data.pop("products_id", [])
        cities_data = validated_data.pop("cities_id", [])
        promo = super().create(validated_data)
        promo.products.set(products_data)
        promo.cities.set(cities_data)
        return promo

    def get_image(self, obj) -> str | None:
        return obj.image.url if obj.image else None

    def update(self, instance, validated_data):
        products_data = validated_data.pop("products_id", [])
        instance = super().update(instance, validated_data)
        instance.products.set(products_data)
        return instance
