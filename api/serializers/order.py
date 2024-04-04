from typing import OrderedDict
from rest_framework import serializers

from cart.models import Order, OrderStatus, ProductsInOrder
from api.serializers import ProductsInOrderSerializer
from api.mixins import ValidateAddressMixin


class OrderStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderStatus
        fields = [
            "name"
        ]

# TODO create ProductOrderSerializer
class OrderSerializer(ValidateAddressMixin, serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status = OrderStatusSerializer(read_only=True)
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
            "status",
        ]

    def get_products(self, obj) -> OrderedDict:
        products_in_order = ProductsInOrder.objects.filter(order=obj)
        return ProductsInOrderSerializer(products_in_order, many=True).data

    def create(self, validated_data):
        validated_data["total"] = 0
        return super().create(validated_data)
