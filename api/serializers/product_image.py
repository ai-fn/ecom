from api.serializers import ActiveModelSerializer

from shop.models import Product, ProductImage
from rest_framework import serializers


class ProductImageSerializer(ActiveModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product", write_only=True)

    class Meta:
        model = ProductImage
        fields = ["id", "name", "thumb_img", "image", "product_id",]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.url if instance.image else None
        return data
