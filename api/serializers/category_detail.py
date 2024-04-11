from rest_framework import serializers

from api.serializers import CategoryMetaDataSerializer
from shop.models import Category


class CategoryDetailSerializer(serializers.ModelSerializer):
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "category_meta",
            "is_popular",
            "is_visible",
            "icon",
            "image_url",
            "order"
        ]
    
    def get_icon(self, obj) -> str:
        return obj.icon.url if obj.icon else None

    def get_image_url(self, obj) -> str:
        return obj.image.url if obj.image else None
