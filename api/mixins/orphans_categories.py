from django.db.models import QuerySet


class CategoriesWithProductsMixin:
    def get_categories_with_products(self, queryset: QuerySet, domain: str):
        return queryset.filter(
            pk__in=[
                t.id
                for t in queryset if t.get_descendants(include_self=True)
                .filter(
                    is_active=True,
                    is_visible=True,
                    products__isnull=False,
                    products__prices__city_group__cities__domain=domain,
                )
                .exists()
            ]
        )
