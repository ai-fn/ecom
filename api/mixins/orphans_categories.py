from django.db.models import QuerySet
from shop.models import Category


class CategoriesWithProductsMixin:
    def get_categories_with_products(self, domain: str, instance: Category = None, queryset: QuerySet = None):
        if all((instance, queryset)):
            raise ValueError("'instance' and 'queryset' could not be settet together.")
        elif not any((instance, queryset)):
            raise ValueError("one of ('instance', 'queryset') must be setted.")

        if instance:
            queryset = Category.objects.filter(pk=instance.pk)

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
