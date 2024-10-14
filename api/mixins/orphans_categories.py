from django.db.models import QuerySet


class GetOrphanCategories:
    def get_orphan_categories(self, queryset: QuerySet, domain: str):
        parents = []
        top_level = queryset.filter(level=0)
        for parent in top_level:
            if parent.get_descendants().filter(
                is_active=True, is_visible=True,
                products__isnull=False,
                products__prices__city_group__cities__domain=domain
            ).exists():
                parents.append(parent.id)
        return queryset.filter(pk__in=parents)
