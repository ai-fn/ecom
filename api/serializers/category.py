from typing import OrderedDict
from rest_framework import serializers

from api.serializers import CategoryMetaDataSerializer
from shop.models import Category, CategoryMetaData


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)
    category_meta_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoryMetaData.objects.all(), write_only=True, many=True, source="category_meta"
    )
    image_url = (
        serializers.SerializerMethodField()
    )  # Добавляем поле для URL изображения
    icon = serializers.SerializerMethodField()
    parents = serializers.SerializerMethodField()  # Добавляем новое поле для родителей
    is_popular = serializers.BooleanField(read_only=True)
    is_visible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "order",
            "parent",
            "children",
            "parents",
            "category_meta",
            "category_meta_id",
            "icon",
            "image_url",
            "is_visible",
            "is_popular",
        ]
    
    def get_icon(self, obj) -> str | None:
        return obj.icon.url if obj.icon else None


    def get_children(self, obj) -> None | OrderedDict:
        if obj.is_leaf_node():
            return None
        return CategorySerializer(obj.get_children(), many=True).data

    def get_image_url(self, obj) -> None | str:
        if obj.image:  # Проверяем, есть ли у категории изображение
            return obj.image.url  # Возвращаем URL изображения
        return None  # Если изображения нет, возвращаем None

    def get_parents(self, obj) -> list:
        """
        Возвращает список родительских категорий в виде кортежей (name, slug, id),
        начиная от корневой категории до текущего родителя.
        """
        parents = []
        current_parent = obj.parent
        while current_parent:
            parents.append(
                (
                    current_parent.name,
                    current_parent.slug,
                    # current_parent.id,
                )
            )
            current_parent = current_parent.parent
        return list(
            reversed(parents)
        )  # Переворачиваем список, чтобы начать с корневого элемента
