from rest_framework import serializers
from api.models import ProductFile, Product


class ProductFileSerializer(serializers.ModelSerializer):

    file = serializers.FileField(write_only=True)
    file_url = serializers.SerializerMethodField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")

    class Meta:
        model = ProductFile
        fields = [
            "id",
            "name",
            "file",
            "file_url",
            "product_id",
        ]

    def get_file_url(self, obj) -> str | None:
        return obj.file.url if obj.file else None
