from rest_framework import serializers

from shop.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source="image")

    class Meta:
        model = ProductImage
        fields = ["image_url"]
