from rest_framework import serializers

from cart.models import Order
from api.serializers import ProductsInOrderSerializer


class OrderSerializer(serializers.ModelSerializer):
    products = ProductsInOrderSerializer()
    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "products",
            "created_at",
        ]
