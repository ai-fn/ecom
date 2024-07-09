from typing import OrderedDict
from rest_framework import serializers

from shop.models import Category


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    parents = serializers.SerializerMethodField()
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
            "icon",
            "image",
            "is_visible",
            "is_popular",
            "thumb_img",
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['icon'] = instance.icon.url if instance.icon else None
        data['image'] = instance.image.url if instance.image else None
        return data
    
    def get_icon_url(self, obj) -> str | None:
        return obj.icon.url if obj.icon else None

    def get_children(self, obj) -> None | OrderedDict:
        if obj.is_leaf_node():
            return None
        return CategorySerializer(obj.get_children(), many=True).data

    def get_image_url(self, obj) -> None | str:
        return obj.image.url if obj.image else None

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
