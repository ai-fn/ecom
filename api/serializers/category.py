from rest_framework import serializers

from api.serializers import CategoryMetaDataSerializer
from shop.models import Category, CategoryMetaData


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)
    parents = serializers.SerializerMethodField()  # Добавляем поле для родителей
    image_url = serializers.SerializerMethodField()  # URL изображения

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "parent",
            "children",
            "parents",  # Добавляем родителей в поля
            "category_meta",
            "icon",
            "image_url",
            "is_visible",
        ]

    def get_children(self, obj):
        if obj.is_leaf_node():
            return None
        return CategorySerializer(
            obj.get_children(), many=True, context=self.context
        ).data

    def get_parents(self, obj):
        # Метод для получения всех родителей до корня
        parents = []
        current_parent = obj.parent
        while current_parent is not None:
            parents.append(
                CategorySerializer(current_parent, context=self.context).data
            )
            current_parent = current_parent.parent
        return parents[::-1]  # Возвращаем в правильном порядке

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None
