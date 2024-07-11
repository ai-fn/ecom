from api.serializers import ActiveModelSerializer

from api.serializers import ProductCatalogSerializer
from cart.models import Order, ProductsInOrder
from shop.models import Product
from rest_framework import serializers


class ProductsInOrderSerializer(ActiveModelSerializer):

    product = ProductCatalogSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True, required=True
    )
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order", write_only=True, required=True
    )

    class Meta:
        model = ProductsInOrder
        fields = [
            "id",
            "order",
            "order_id",
            "product",
            "product_id",
            "quantity",
            "price",
        ]
