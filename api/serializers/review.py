from rest_framework import serializers

from shop.models import Review
from api.serializers import UserReviewSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user = UserReviewSerializer()
    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "rating",
            "review",
            "created_at",
        ]
