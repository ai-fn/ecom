from shop.models import CharacteristicValue
from django_filters import rest_framework as filters


class CharacteristicValueFilters(filters.FilterSet):

    unique = filters.BooleanFilter(method="unique_filter")

    class Meta:
        model = CharacteristicValue
        fields = ["characteristic", "product", "value", "slug", "created_at", "updated_at", "unique"]
    
    def unique_filter(self, queryset, name, value):
        if value:
            return queryset.distinct()
        
        return queryset
