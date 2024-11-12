from typing import OrderedDict

from django.db.models import F
from rest_framework import serializers

from cart.models import Order, OrderStatus, ProductsInOrder
from api.serializers import ProductsInOrderSerializer
from api.mixins import ValidateAddressMixin, ValidatePhoneNumberMixin
from api.serializers import ActiveModelSerializer


class OrderStatusSerializer(ActiveModelSerializer):

    class Meta:
        model = OrderStatus
        fields = ["name"]


class OrderSerializer(ValidateAddressMixin, ActiveModelSerializer, ValidatePhoneNumberMixin):
    products = serializers.SerializerMethodField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total",
            "status",
            "address",
            "customer",
            "products",
            "created_at",
            "delivery_type",
            "receiver_phone",
            "receiver_email",
            "receiver_last_name",
            "receiver_first_name",
        ]

    def get_products(self, obj) -> OrderedDict:
        products_in_order = (
            ProductsInOrder.objects.filter(order=obj)
            .prefetch_related("product__category")
            .annotate(product__category_slug=F("product__category__slug"))
        )
        return ProductsInOrderSerializer(products_in_order, many=True).data

    def validate_reveiver_phone(self, value):
        self.phone_is_valid(value)
        return value

    def create(self, validated_data):
        validated_data["total"] = 0
        return super().create(validated_data)


class OrderSelectedSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ["cartitem_ids"]
