from rest_framework import serializers

from shop.models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product", write_only=True)

    class Meta:
        model = ProductImage
        fields = ["id", "name", "thumb_img", "image", "image_url", "product_id",]

    def get_image_url(self, obj) -> str:
        return obj.image.url if obj.image else None
