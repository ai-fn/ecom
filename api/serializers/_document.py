from api.serializers.price import PriceSerializer
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from api.serializers import ProductCatalogSerializer, UserSerializer
from shop.documents import BrandDocument, CategoryDocument, ReviewDocument
from rest_framework import serializers

from shop.models import Product


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


class CategoryDocumentSerializer(DocumentSerializer):
    image = serializers.ImageField()

    class Meta:
        document = CategoryDocument
        fields = "__all__"


class BrandDocumentSerializer(DocumentSerializer):

    class Meta:
        document = BrandDocument
        fields = "__all__"


class ProductDocumentSerializer(serializers.ModelSerializer):
    category_slug = serializers.SlugField(
        source="category.slug",
        read_only=True,
    )
    price = PriceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "search_image",
            "thumb_img",
            "category_slug",
            "slug",
            "price",
        ]


class ReviewDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ReviewDocument
        fields = "__all__"
