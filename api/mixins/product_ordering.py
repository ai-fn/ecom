from loguru import logger
from django.db.models import Case, When, BooleanField, F


class ProductSorting:
    sorted_fields = (
        "price",
        "is_new",
        "rating",
        "in_promo",
        "is_popular",
    )

    def sorted_queryset(self, queryset):
        ordering: str = self.request.query_params.get("order_by")
        if not ordering:
            return queryset

        self.city_domain = self.request.query_params.get("city_domain")
        self.reversed_prefix = "-" if ordering.startswith("-") else ""
        ordering = ordering.lstrip("-")
        self.queryset = queryset

        if not ordering in self.sorted_fields:
            logger.info(
                f"Unable to sort by field '{ordering}', it should be one of '{self.sorted_fields}'"
            )
            return queryset

        if hasattr(self, f"_sort_{ordering}"):
            func = getattr(self, f"_sort_{ordering}")
            queryset = func()
            return queryset
        else:
            return queryset.order_by(f"{self.reversed_prefix}{ordering}")

    def _sort_price(self):
        if self.city_domain:
            return self.queryset.order_by(
                f"{self.reversed_prefix}prices__price"
            ).distinct()
        else:
            return self.queryset

    def _sort_rating(self):
        return self.queryset.order_by(
            f"{self.reversed_prefix}reviews__rating"
        ).distinct()

    def _sort_in_promo(self):
        if self.city_domain:
            return self.queryset.annotate(
                in_promo=Case(
                    When(prices__price__lt=F("prices__old_price"), then=True),
                    default=False,
                    output_field=BooleanField(),
                )
            ).order_by(f"{self.reversed_prefix}in_promo")
        else:
            return self.queryset
