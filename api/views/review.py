from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.review import ReviewSerializer
from shop.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
    """Возвращает отзывы

    Args:
        viewsets (_type_): _description_
    """

    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

