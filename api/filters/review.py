from shop.models import Review
from django_filters import rest_framework as filters


class ReviewFilters(filters.FilterSet):

    class Meta:
        model = Review
        fields = ["product", "user", "rating",]
