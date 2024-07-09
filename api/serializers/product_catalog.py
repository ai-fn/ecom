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

    cart_quantity = serializers.IntegerField(min_value=1, read_only=True)
    in_promo = serializers.SerializerMethodField()

    def get_category_slug(self, obj) -> str:
        return obj.category.slug if obj.category else None
    
    def get_in_promo(self, obj) -> bool:
        if (price := self.get_city_price(obj)) and (old_price := self.get_old_price(obj)):
            return price < old_price
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for attr in ("catalog_image", "search_image", "original_image"):
            val = getattr(instance, attr, None)
            data[attr] = getattr(val, "url", None)

        return data

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
            "original_image",
            "cart_quantity",
            "is_popular",
            "is_new",
            "thumb_img",
            "description",
            "in_promo",
            "priority",
        ]
