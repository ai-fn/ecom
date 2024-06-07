from rest_framework import serializers
from cart.models import CartItem, Product
from api.serializers import ProductCatalogSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCatalogSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source="product"
    )
    quantity = serializers.IntegerField(max_value=999999, min_value=1)
    city_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        read_only=True,
    )
    old_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "city_price", "old_price"]
        read_only_fields = ("id",)

    def create(self, validated_data):
        request = self.context.get("request", None)
        customer = request.user  # Assuming the customer is the logged-in user

        # Remove 'customer' from validated_data if it exists to avoid conflict
        validated_data.pop(
            "customer", None
        )  # This removes 'customer' if it's present, and does nothing if it's not

        # Now create the CartItem with the customer set to the current user and the rest from validated_data
        queryset = CartItem.objects.filter(customer=customer, product=validated_data['product'])
        if not queryset.exists():
            cart_item = CartItem.objects.create(customer=customer, **validated_data)
        else:
            cart_item = queryset.first()
            cart_item.quantity = validated_data['quantity']
            cart_item.save()

        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save(update_fields=["quantity"])
        return instance


class SimplifiedCartItemSerializer(serializers.ModelSerializer):

    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']