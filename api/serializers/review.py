from rest_framework import serializers

from shop.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "name",
            "rating",
            "review",
            "created_at",
        ]
