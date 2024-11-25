from loguru import logger
from api.serializers import ActiveModelSerializer

from shop.models import Product
from rest_framework import serializers
from django.db.models import Sum


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

    def check_price(self, instance):
        fields = {"city_price": "price", "old_price": "old_price"}
        domain = self.context.get("city_domain")
        if not all([hasattr(instance, field) for field in fields.keys()]):
            price = instance.prices.filter(city_group__cities__domain=domain).first()
            for field in fields:
                if not hasattr(instance, field):
                    value = getattr(price, fields[field], None)
                    setattr(instance, field, value)
        
 
    def check_rating(self, instance):
        if not hasattr(instance, "reviews_count"):
            setattr(instance, "reviews_count", instance.reviews.count())

        if not hasattr(instance, "rating"):
            value = 0
            t_rating = instance.reviews.aggregate(sum_rating=Sum("rating"))["sum_rating"] or 0
            if instance.reviews_count > 0:
                value = t_rating / instance.reviews_count

            setattr(instance, "rating", value)


    def to_representation(self, instance):
        check_fields = ("price", "rating")
        for field in check_fields:
            func = getattr(self, f"check_{field}")
            func(instance)

        data = super().to_representation(instance)
        val = getattr(instance, "catalog_image", None)
        data["catalog_image"] = val.url if val and hasattr(val, "url") else None

        in_promo = False
        if (cp := data["city_price"]) and (op := data["old_price"]):
            in_promo = cp < op

        data["in_promo"] = in_promo

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
            "unit",
            "in_promo",
            "rating",
            "reviews_count",
        ]
