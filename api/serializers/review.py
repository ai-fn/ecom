from api.serializers import ActiveModelSerializer

from shop.models import Review
from api.serializers import UserReviewSerializer


class ReviewSerializer(ActiveModelSerializer):
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
