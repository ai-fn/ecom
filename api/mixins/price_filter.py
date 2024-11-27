from typing import Optional
from django.core.exceptions import FieldError
from django.db.models import QuerySet
from loguru import logger


class PriceFilterMixin:
    """
    Mixin для фильтрации продуктов, имеющих цену, в зависимости от заданного домена.
    """

    def get_products_only_with_price(
        self, queryset: QuerySet, domain: Optional[str] = "", prefix: str = ""
    ) -> QuerySet:
        """
        Возвращает продукты, у которых есть цена, соответствующая заданному домену.

        :param queryset: QuerySet продуктов для фильтрации.
        :type queryset: QuerySet
        :param domain: Домен для фильтрации цен. Если не указан, используется пустая строка.
        :type domain: str, optional
        :param prefix: Префикс для фильтруемых полей. По умолчанию пустой.
        :type prefix: str
        :return: Отфильтрованный QuerySet продуктов с ценами.
        :rtype: QuerySet
        """
        try:
            q = {f"{prefix}city_price__gt": 0}
            queryset = queryset.filter(**q)
        except FieldError:
            q = {f"{prefix}prices__city_group__cities__domain": domain}
            queryset = queryset.filter(**q)
        except Exception as err:
            logger.error(f"Error while getting only products with price: '{str(err)}'")
        return queryset
