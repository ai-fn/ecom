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

    catalog_image_url = serializers.SerializerMethodField(read_only=True)
    search_image_url = serializers.SerializerMethodField(read_only=True)
    original_image_url = serializers.SerializerMethodField(read_only=True)
    catalog_image = serializers.ImageField(write_only=True)
    search_image = serializers.ImageField(write_only=True)
    original_image = serializers.ImageField(write_only=True)

    cart_quantity = serializers.IntegerField(min_value=1, read_only=True)
    in_promo = serializers.SerializerMethodField()

    def get_category_slug(self, obj) -> str:
        return obj.category.slug if obj.category else None

    def get_catalog_image_url(self, obj) -> str:
        return obj.catalog_image.url if obj.catalog_image else None

    def get_search_image_url(self, obj) -> str:
        return obj.search_image.url if obj.search_image else None

    def get_original_image_url(self, obj) -> str:
        return obj.original_image.url if obj.original_image else None
    
    def get_in_promo(self, obj) -> bool:
        if (price := self.get_city_price(obj)) and (old_price := self.get_old_price(obj)):
            return price < old_price
        return False

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
            "search_image_url",
            "original_image_url",           
            "catalog_image_url",
            "original_image",
            "cart_quantity",
            "is_popular",
            "is_new",
            "thumb_img",
            "description",
            "in_promo",
            "priority",
        ]
