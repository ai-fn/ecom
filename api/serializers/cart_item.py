from rest_framework import serializers
from cart.models import CartItem, Product
from api.serializers import ProductCatalogSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCatalogSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_id',
            'quantity'
        ]
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        cart_item = CartItem.objects.create(**validated_data)
        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save(updated_fields=['quantity'])
        return instance
