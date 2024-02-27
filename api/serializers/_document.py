from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from api.serializers.product_image import ProductImageSerializer

from shop.documents import CategoryDocument, ProductDocument, ReviewDocument
from rest_framework import serializers

from shop.models import Product


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


class CategoryDocumentSerializer(DocumentSerializer):
    image = serializers.ImageField()

    class Meta:
        document = CategoryDocument
        fields = "__all__"


class ProductDocumentSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "images",  # Ensure images are included
        ]


class ReviewDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ReviewDocument
        fields = "__all__"
