from rest_framework import serializers

from api.serializers import CategoryMetaDataSerializer
from shop.models import Category

class CategoryDetailSerializer(serializers.ModelSerializer):
    category_meta = CategoryMetaDataSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "category_meta"]
