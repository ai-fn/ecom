from cart.models import ProductsInOrder

from rest_framework import serializers


class ProductsInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsInOrder
        fields = [
            "id",
            "order",
            "product",
            "quantity",
            "created_at",
        ]
