from typing import OrderedDict
from api.serializers import ActiveModelSerializer
from rest_framework import serializers
from shop.models import Category


class CategorySerializer(ActiveModelSerializer):
    children = serializers.SerializerMethodField()

    parents = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "h1_tag",
            "slug",
            "order",
            "parent",
            "description",
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
        data["icon"] = instance.icon.url if instance.icon else None
        data["image"] = instance.image.url if instance.image else None
        return data

    def get_children(self, obj) -> None | OrderedDict:
        if obj.is_leaf_node():
            return None
        return CategorySerializer(obj.get_children(), many=True).data

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
        return list(reversed(parents))


class CategorySimplifiedSerializer(ActiveModelSerializer):
    parents = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "icon",
            "image",
            "order",
            "parent",
            "parents",
            "thumb_img",
            "is_visible",
            "is_popular",
            "description",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["icon"] = instance.icon.url if instance.icon else None
        data["image"] = instance.image.url if instance.image else None
        return data

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
        return list(reversed(parents))


class CategorySliderSerializer(ActiveModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "icon",
            "image",
            "is_popular",
            "thumb_img",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["icon"] = instance.icon.url if instance.icon else None
        data["image"] = instance.image.url if instance.image else None
        return data


class CategoryOrphanSerializer(CategorySliderSerializer):

    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "children",
            "icon",
            "image",
        ]

    def get_children(self, obj) -> None | OrderedDict:
        domain = self.context.get("city_domain", "")
        return (
            obj.get_descendants()
            .filter(
                is_active=True,
                is_visible=True,
                products__isnull=False,
                products__prices__city_group__cities__domain=domain,
            )
            .values("id", "name", "slug")
            .distinct()
        )
