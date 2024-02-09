from rest_framework import serializers

from shop.models import CategoryMetaData


class CategoryMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryMetaData
        fields = ["title", "description"]
