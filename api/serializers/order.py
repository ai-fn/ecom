from typing import OrderedDict
from rest_framework import serializers

from django.db.models import F

from cart.models import Order
from api.serializers import ProductCatalogSerializer
from api.mixins import ValidateAddressMixin
from shop.models import Product


class OrderSerializer(ValidateAddressMixin, serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "products",
            "created_at",
            "region",
            "district",
            "city_name",
            "street",
            "house",
            "total",
        ]
        
    def get_products(self, obj) -> OrderedDict:
        products_in_order = Product.objects.filter(count_in_order__order=obj).annotate(cart_quantity=F("count_in_order__quantity"), city_price=F("count_in_order__price"))
        return ProductCatalogSerializer(products_in_order, many=True).data

    def create(self, validated_data):
        validated_data["total"] = 0
        return super().create(validated_data)
