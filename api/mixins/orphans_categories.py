from typing import Optional
from django.db.models import QuerySet
from shop.models import Category


class CategoriesWithProductsMixin:
    """
    Mixin для получения категорий, содержащих продукты, соответствующие указанному домену.
    """

    def get_categories_with_products(
        self, domain: str, queryset: Optional[QuerySet] = None
    ) -> QuerySet:
        """
        Возвращает категории, содержащие активные и видимые продукты, доступные в указанном домене.

        :param domain: Домен для фильтрации продуктов.
        :type domain: str
        :param queryset: QuerySet категорий для фильтрации.
        :type queryset: QuerySet, optional
        :return: Отфильтрованный QuerySet категорий.
        :rtype: QuerySet
        """
        if queryset is None or not queryset.exists():
            return queryset

        return queryset.filter(
            pk__in=[
                t.id
                for t in queryset
                if t.get_descendants(include_self=True)
                .filter(
                    is_active=True,
                    is_visible=True,
                    products__isnull=False,
                    products__prices__city_group__cities__domain=domain,
                )
                .exists()
            ]
        )
