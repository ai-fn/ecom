from rest_framework import serializers

from api.serializers import CategoryMetaDataSerializer
from shop.models import Category, CategoryMetaData

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)
    category_meta_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoryMetaData.objects.all(), write_only=True, source="category_meta"
    )

    image_url = (
        serializers.SerializerMethodField()
    )  # Добавляем поле для URL изображения

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "children",
            "category_meta",
            "category_meta_id",
            "icon",
            "image_url",
            "is_visible",
        ]

    def get_children(self, obj):
        if obj.is_leaf_node():
            return None
        return CategorySerializer(obj.get_children(), many=True).data

    def get_image_url(self, obj):
        if obj.image:  # Проверяем, есть ли у категории изображение
            return obj.image.url  # Возвращаем URL изображения
        return None  # Если изображения нет, возвращаем None
