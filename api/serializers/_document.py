from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from shop.documents import CategoryDocument, ProductDocument, ReviewDocument


class CategoryDocumentSerializer(DocumentSerializer):
    class Meta:
        document = CategoryDocument
        fields = "__all__"


class ProductDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ProductDocument
        fields = "__all__"


class ReviewDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ReviewDocument
        fields = "__all__"
