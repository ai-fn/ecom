from shop.models import Review
from django_filters import rest_framework as filters


class ReviewFilters(filters.FilterSet):
    """
    Фильтр-сет для модели Review.

    Позволяет фильтровать отзывы по продукту, пользователю и рейтингу.
    """

    class Meta:
        model = Review
        fields = ["product", "user", "rating",]
