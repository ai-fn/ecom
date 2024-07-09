from rest_framework import serializers
from api.models import ProductFile, Product


class ProductFileSerializer(serializers.ModelSerializer):

    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")

    class Meta:
        model = ProductFile
        fields = [
            "id",
            "name",
            "file",
            "product_id",
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file'] = instance.file.url if instance.file else None
        return data
