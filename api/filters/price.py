from django_filters import rest_framework as filters

from shop.models import Price


class PriceFilter(filters.FilterSet):
    class Meta:
        model = Price
        fields = ["city_group"]
