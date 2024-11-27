from typing import List
from django.db.models import F, Sum, Count, Avg, Value, QuerySet


class AnnotateProductMixin:
    """
    Mixin для добавления аннотаций в QuerySet модели Product.

    Поддерживает аннотации для цен, рейтинга, количества в корзине и других характеристик.
    """

    def annotate_queryset(self, queryset, prefix: str = "", fields: List[str] = None):
        """
        Аннотирует QuerySet указанными полями.

        :param queryset: QuerySet, к которому будут добавлены аннотации.
        :param prefix: Префикс для аннотируемых полей.
        :type prefix: str
        :param fields: Список полей для аннотирования. Если не указан, используется список по умолчанию.
        :type fields: List[str], optional
        :return: Аннотированный QuerySet.
        :rtype: QuerySet
        """
        if fields is None:
            fields = ("prices", "rating", "cart_quantity")

        for field in fields:
            method_name = f"_annotate_{field}"
            if hasattr(self, method_name):
                func = getattr(self, method_name)
                queryset = func(queryset, prefix)

        queryset = queryset.annotate(**{f"{prefix}category_slug": F(f"{prefix}category__slug")})
        return queryset

    def _annotate_cart_quantity(self, queryset, prefix: str = "") -> QuerySet:
        """
        Аннотирует QuerySet количеством товаров в корзине текущего пользователя.

        :param queryset: QuerySet для аннотирования.
        :param prefix: Префикс для аннотируемых полей.
        :type prefix: str
        :return: Аннотированный QuerySet.
        :rtype: QuerySet
        """
        if hasattr(self, "request") and self.request.user.is_authenticated:
            queryset = (
                queryset.prefetch_related(f"{prefix}cart_items")
                .annotate(
                    cart_quantity=Sum(
                        f"{prefix}cart_items__quantity",
                        filter=F(f"{prefix}cart_items__customer_id") == self.request.user.id,
                    )
                )
            )
        return queryset

    def _annotate_prices(self, queryset, prefix: str = "") -> QuerySet:
        """
        Аннотирует QuerySet текущей и старой ценами для указанного домена города.

        :param queryset: QuerySet для аннотирования.
        :param prefix: Префикс для аннотируемых полей.
        :type prefix: str
        :return: Аннотированный QuerySet.
        :rtype: QuerySet
        """
        if not hasattr(self, "request"):
            return queryset

        domain = self.request.query_params.get("city_domain")
        if not domain:
            queryset = queryset.annotate(
                **{f"{prefix}city_price": Value(0), f"{prefix}old_price": Value(0)}
            )
            return queryset

        fields = {
            f"{prefix}city_price": F(f"{prefix}prices__price"),
            f"{prefix}old_price": F(f"{prefix}prices__old_price"),
        }
        queryset = (
            queryset.prefetch_related(f"{prefix}prices")
            .annotate(**fields)
            .distinct()
        )
        return queryset

    def _annotate_rating(self, queryset, prefix: str = "") -> QuerySet:
        """
        Аннотирует QuerySet рейтингом и количеством отзывов.

        :param queryset: QuerySet для аннотирования.
        :param prefix: Префикс для аннотируемых полей.
        :type prefix: str
        :return: Аннотированный QuerySet.
        :rtype: QuerySet
        """
        fields = {
            f"{prefix}rating": Avg(f"{prefix}reviews__rating"),
            f"{prefix}reviews_count": Count(f"{prefix}reviews"),
        }
        queryset = queryset.prefetch_related(f"{prefix}reviews").annotate(**fields)
        return queryset
