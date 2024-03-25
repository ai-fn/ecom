from rest_framework import serializers

from cart.models import Order, ProductsInOrder
from api.serializers import ProductsInOrderSerializer
from api.mixins import ValidateAddressMixin


class OrderSerializer(serializers.ModelSerializer, ValidateAddressMixin):
    products = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "products",
            "address",
            "created_at",
        ]
        
    def get_products(self, obj):
        products_in_order = ProductsInOrder.objects.filter(order=obj)
        return ProductsInOrderSerializer(products_in_order, many=True).data