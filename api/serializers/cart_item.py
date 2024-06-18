from rest_framework import serializers
from cart.models import CartItem, Product
from api.serializers import ProductCatalogSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCatalogSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source="product"
    )
    quantity = serializers.IntegerField(max_value=999999, min_value=1)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", ]
        read_only_fields = ("id",)

    def create(self, validated_data):
        request = self.context.get("request", None)
        customer = request.user

        validated_data.pop(
            "customer", None
        )

        queryset = CartItem.objects.filter(
            customer=customer, product=validated_data["product"]
        )
        if not queryset.exists():
            cart_item = CartItem.objects.create(customer=customer, **validated_data)
        else:
            cart_item = queryset.first()
            cart_item.quantity = validated_data["quantity"]
            cart_item.save()

        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save(update_fields=["quantity"])
        return instance


class SimplifiedCartItemSerializer(serializers.ModelSerializer):

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product"
    )

    class Meta:
        model = CartItem
        fields = ["product_id", "quantity"]
