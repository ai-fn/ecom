from rest_framework import serializers
from cart.models import CartItem, Product
from api.serializers import ProductCatalogSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCatalogSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source="product"
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity"]
        read_only_fields = ("id",)

    def create(self, validated_data):
        request = self.context.get("request", None)
        customer = request.user  # Assuming the customer is the logged-in user

        # Remove 'customer' from validated_data if it exists to avoid conflict
        validated_data.pop(
            "customer", None
        )  # This removes 'customer' if it's present, and does nothing if it's not

        # Now create the CartItem with the customer set to the current user and the rest from validated_data
        cart_item = CartItem.objects.create(customer=customer, **validated_data)

        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save(update_fields=["quantity"])
        return instance
