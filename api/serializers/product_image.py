from rest_framework import serializers

from shop.models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["image_url", "thumb_img",]

    def get_image_url(self, obj) -> str:
        return obj.image.url if obj.image else None
