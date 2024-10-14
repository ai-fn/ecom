from django.db.models import QuerySet


class GetOrphanCategories:
    def get_orphan_categories(self, queryset: QuerySet, domain: str):
        queryset = queryset.filter(
            is_active=True,
            is_visible=True,
            parent__isnull=True,
            products__isnull=False,
            children__products__prices__city_group__cities__domain=domain,
        )
        return queryset