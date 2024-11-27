from django_filters import rest_framework as filters

from shop.models import Price


class PriceFilter(filters.FilterSet):
    """
    Фильтр-сет для модели Price.

    Позволяет фильтровать цены на основе группы городов.
    """

    class Meta:
        model = Price
        fields = ["city_group"]
