from typing import OrderedDict
from rest_framework import serializers

from cart.models import Order, ProductsInOrder
from api.serializers import ProductsInOrderSerializer
from api.mixins import ValidateAddressMixin


class OrderSerializer(ValidateAddressMixin, serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
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
        ]
        
    def get_products(self, obj) -> OrderedDict:
        products_in_order = ProductsInOrder.objects.filter(order=obj)
        return ProductsInOrderSerializer(products_in_order, many=True).data