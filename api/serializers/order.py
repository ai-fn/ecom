from rest_framework import serializers

from cart.models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "products",
            "created_at",
        ]
