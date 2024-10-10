from django.db.models import QuerySet


class PriceFilterMixin:
    def get_products_only_with_price(self, queryset: QuerySet, domain: str, prefix: str = "") -> QuerySet:
        q = {f"{prefix}prices__city_group__cities__domain": domain}
        queryset = queryset.filter(**q)
        return queryset
