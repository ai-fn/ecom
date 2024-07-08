from rest_framework import serializers

from api.serializers import CategoryMetaDataSerializer
from shop.models import Category


class CategoryDetailSerializer(serializers.ModelSerializer):
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    icon_url = serializers.SerializerMethodField(read_only=True)
    image = serializers.ImageField(write_only=True)
    icon = serializers.FileField(write_only=True)

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
            "image",
            "icon_url",
            "image_url",
            "order",
            "thumb_img",
        ]

    def get_icon_url(self, obj) -> str:
        return obj.icon.url if obj.icon else None

    def get_image_url(self, obj) -> str:
        return obj.image.url if obj.image else None
