from rest_framework import serializers

from shop.models import CategoryMetaData


class CategoryMetaDataSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = CategoryMetaData
        fields = ["title", "description", "category_id"]
