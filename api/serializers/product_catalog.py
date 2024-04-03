from rest_framework import serializers

from api.serializers import ProductImageSerializer
from shop.models import Price, Product


class ProductCatalogSerializer(serializers.ModelSerializer):
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

    def get_category_slug(self, obj) -> str:
        return obj.category.slug

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
            "in_stock",
            "category_slug",
            "brand_slug",
            "search_image",
            "catalog_image",
            "cart_quantity",
            "is_popular",
        ]

    def get_city_price(self, obj):
        city_domain = self.context.get('city_domain')
        if city_domain:
            price = Price.objects.filter(city__domain=city_domain, product=obj).first()
            if price:
                return price.price
        return None

    def get_old_price(self, obj):
        city_domain = self.context.get('city_domain')
        if city_domain:
            price = Price.objects.filter(city__domain=city_domain, product=obj).first()
            if price:
                return price.old_price
        return None
