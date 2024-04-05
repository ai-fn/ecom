from rest_framework import serializers

from api.serializers import ProductCatalogSerializer
from cart.models import ProductsInOrder


class ProductsInOrderSerializer(serializers.ModelSerializer):

    product = ProductCatalogSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductsInOrder.objects.all(), write_only=True, required=True
    )

    class Meta:
        model = ProductsInOrder
        fields = [
            "id",
            "order",
            "product",
            "product_id",
            "quantity",
            "price",
        ]
