from api.serializers import ActiveModelSerializer

from api.mixins import SerializerGetPricesMixin, RatingMixin
from api.serializers import ProductImageSerializer
from shop.models import Product
from rest_framework import serializers


class ProductCatalogSerializer(ActiveModelSerializer):
    city_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    old_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_slug = serializers.SerializerMethodField()

    cart_quantity = serializers.IntegerField(min_value=1, read_only=True)
    in_promo = serializers.SerializerMethodField()
    rating = serializers.FloatField()
    reviews_count = serializers.IntegerField()

    def get_category_slug(self, obj) -> str:
        return obj.category.slug if obj.category else None

    def get_in_promo(self, obj) -> bool:
        return True #

    def to_representation(self, instance):
        data = super().to_representation(instance)
        val = getattr(instance, "catalog_image", None)
        data["catalog_image"] = val.url if val and hasattr(val, "url") else None
        data["in_promo"] = data["city_price"] < data["old_price"]
        return data

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "article",
            "slug",
            "city_price",
            "old_price",
            "in_stock",
            "category_slug",
            "catalog_image",
            "cart_quantity",
            "is_popular",
            "is_new",
            "in_promo",
            "rating",
            "reviews_count",
        ]
