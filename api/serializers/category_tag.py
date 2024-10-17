from rest_framework import serializers
from shop.models import CategoryTag


class CategoryTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTag
        fields = [
            "id",
            "name",
            "parent",
            "category_slug",
        ]


class CategoryTagDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTag
        fields = [
            "id",
            "name",
            "order",
            "parent",
            "category_slug",
            "is_active",
            "created_at",
            "updated_at",
            "category_slug",
        ]
