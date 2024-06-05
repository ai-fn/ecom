from rest_framework import serializers

from api.mixins import SerializerGetPricesMixin
from api.serializers import ProductImageSerializer
from shop.models import Product


class ProductCatalogSerializer(SerializerGetPricesMixin, serializers.ModelSerializer):
    images = ProductImageSerializer(
        many=True,
        read_only=True,
    )
    city_price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()
    brand_slug = serializers.SlugField(
        source="brand.slug",
        read_only=True
    )
    catalog_image = serializers.SerializerMethodField()
    search_image = serializers.SerializerMethodField()
    cart_quantity = serializers.IntegerField(min_value=1, read_only=True)

    def get_category_slug(self, obj) -> str:
        return obj.category.slug if obj.category else None

    def get_catalog_image(self, obj) -> str:
        return obj.catalog_image.url if obj.catalog_image else None

    def get_search_image(self, obj) -> str:
        return obj.search_image.url if obj.search_image else None

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "brand",
            "article",
            "slug",
            "city_price",
            "old_price",
            "images",
            "in_stock",
            "category_slug",
            "brand_slug",
            "search_image",
            "catalog_image",
            "cart_quantity",
            "is_popular",
            "is_new",
            "thumb_img",
            "description",
        ]
