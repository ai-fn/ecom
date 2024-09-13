from rest_framework import serializers

from api.serializers.price import PriceSerializer

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from shop.documents import BrandDocument, CategoryDocument, ProductDocument


class CategoryDocumentSerializer(DocumentSerializer):
    image = serializers.ImageField()
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        document = CategoryDocument
        fields = [
            "id",
            "name",
            "description",
            "image",
            "slug",
        ]


class BrandDocumentSerializer(DocumentSerializer):

    class Meta:
        document = BrandDocument
        fields = "__all__"


class ProductDocumentSerializer(DocumentSerializer):
    category_slug = serializers.SlugField(
        source="category.slug",
        read_only=True,
    )
    price = serializers.SerializerMethodField()
    search_image = serializers.SerializerMethodField()

    class Meta:
        document = ProductDocument
        fields = [
            "id",
            "title",
            "article",
            "description",
            "search_image",
            "thumb_img",
            "category_slug",
            "slug",
            "price",
        ]

    def get_search_image(self, obj):
        return obj.search_image.url if obj.search_image else None

    def get_price(self, obj):
        return PriceSerializer(
            (
                obj.prices.select_related("city_group__main_city")
                .filter(city_group__main_city__domain=self.context.get("city_domain"))
                .first()
            )
        ).data
