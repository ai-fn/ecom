from api.serializers import ActiveModelSerializer

from cart.models import Order, ProductsInOrder
from shop.models import Product
from rest_framework import serializers


class ProductOrderSerializer(ActiveModelSerializer):
    category_slug = serializers.SlugField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "category_slug",
            "catalog_image",
            "slug",
            "in_stock",
        ]

    def to_representation(self, instance):
        if not hasattr(instance, "category_slug"):
            instance.category_slug = instance.category.slug

        data = super().to_representation(instance)
        data["catalog_image"] = instance.catalog_image.url if instance.catalog_image else None
        return data


class ProductsInOrderSerializer(ActiveModelSerializer):

    product = ProductOrderSerializer(read_only=True)
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
