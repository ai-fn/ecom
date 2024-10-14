from django.core.exceptions import FieldError
from django.db.models import QuerySet
from loguru import logger


class PriceFilterMixin:
    def get_products_only_with_price(self, queryset: QuerySet, domain: str = "", prefix: str = "") -> QuerySet:
        try:
            q = {f"{prefix}city_price__gt": 0}
            queryset = queryset.filter(**q)
        except FieldError:
            q = {f"{prefix}prices__city_group__cities__domain": domain}
            queryset = queryset.filter(**q)
        except Exception as err:
            logger.error(f"Error while getting only products with price: '{str(err)}'")
        return queryset
