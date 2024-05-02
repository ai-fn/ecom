from django_filters.rest_framework import FilterSet

from shop.models import Price

class PriceFilter(FilterSet):
    class Meta:
        model = Price
        fields = ["city_group"]