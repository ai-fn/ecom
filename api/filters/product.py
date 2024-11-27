from django_filters import rest_framework as filters
from django.db.models import Q, Min, Max, QuerySet

from account.models import CityGroup
from shop.models import Category, Characteristic, Product
from api.mixins import GeneralSearchMixin


class ProductFilter(GeneralSearchMixin, filters.FilterSet):
    """
    Фильтр-сет для модели Product.

    Позволяет фильтровать товары по цене, бренду, категории, характеристикам и строковому поиску.
    """

    price_lte = filters.NumberFilter(field_name="prices__price", lookup_expr="lte")
    price_gte = filters.NumberFilter(field_name="prices__price", lookup_expr="gte")
    brand_slug = filters.CharFilter(method="filter_brand_slug")
    category = filters.CharFilter(method="filter_category")
    characteristics = filters.CharFilter(
        method="filter_characteristics", label="Значения характеристик"
    )
    brand_filter = filters.CharFilter(method="filter_brand")
    search = filters.CharFilter(method="filter_search")

    def __init__(
        self,
        data=None,
        queryset=None,
        *,
        request=None,
        prefix=None,
        city_domain: str = None,
        view=None,
    ):
        """
        Инициализация фильтра.

        :param data: Данные для фильтрации.
        :param queryset: Набор данных для фильтрации.
        :param request: HTTP-запрос.
        :param prefix: Префикс для параметров фильтрации.
        :param city_domain: Доменный регион для фильтрации.
        :param view: Связанный ViewSet.
        """

        super().__init__(data, queryset, request=request, prefix=prefix)
        self.city_domain = city_domain
        self.view = view

    class Meta:
        model = Product
        fields = [
            "brand_slug",
            "category",
            "price_lte",
            "price_gte",
            "search",
            "characteristics",
        ]

    @property
    def chars(self):
        """
        Возвращает характеристики для фильтрации.
        """

        if not getattr(self, "_chars", None):
            self._chars = self._get_chars()

        return self._chars

    @property
    def brands(self):
        """
        Возвращает бренды для фильтрации.
        """

        if not getattr(self, "_brands", None):
            self._brands = self._get_brands()

        return self._brands

    @property
    def count(self):
        """
        Возвращает количество отфильтрованных объектов.
        """

        if not getattr(self, "_count", None):
            self._count = self.qs.count()

        return self._count

    def filter_brand_slug(self, queryset, name, value):
        """
        Фильтрует товары по слагу бренда.
        """

        queryset = queryset.filter(brand__slug=value)
        if not all((self.data.get("category"), self.data.get("search`"))):
            self._chars = self._get_chars(queryset)

        return queryset

    def filter_brand(self, queryset, name, value):
        """
        Фильтрует товары по нескольким слагам брендов.
        """

        brand_slugs = value.split(",")
        queryset = queryset.filter(brand__slug__in=brand_slugs)

        return queryset

    def filter_queryset(self, queryset):
        """
        Применяет фильтры к QuerySet.

        Также выполняет агрегаты для минимальной и максимальной цены.
        """

        for name, value in self.form.cleaned_data.items():
            if name not in ("price_lte", "price_gte") and value is not None:
                queryset = self.filters[name].filter(queryset, value)

        aggregates = queryset.aggregate(
            min_price=Min("prices__price"), max_price=Max("prices__price")
        )

        self.min_price = aggregates["min_price"] or 0
        self.max_price = aggregates["max_price"] or 0

        queryset = self.apply_price_filters(queryset)

        return queryset

    def apply_price_filters(self, queryset):
        """
        Применяет фильтры по цене.
        """

        gte_data = self.data.get("price_gte")
        lte_data = self.data.get("price_lte")
        price_filter = Q()

        if lte_data is not None:
            price_filter &= Q(prices__price__lte=lte_data)
        if gte_data is not None:
            price_filter &= Q(prices__price__gte=gte_data)

        return queryset.filter(price_filter)

    def filter_search(self, queryset, name, value):
        """
        Выполняет полнотекстовый поиск по товарам.
        """

        ordering = self.request.query_params.get("order_by")
        page = int(self.request.query_params.get("page", 1))

        cg_domain = CityGroup.get_main_city_domain(domain=self.city_domain)

        search_results, total_result = self.g_search(
            value,
            cg_domain,
            exclude_=("brands", "categories"),
            page=page,
            ordering=ordering,
        )
        queryset = search_results["products"]["queryset"].filter(pk__in=queryset)
        if self.city_domain:
            queryset = queryset.exclude(unavailable_in__domain=self.city_domain)

        self._brands = self._get_brands(queryset)
        self._chars = self._get_chars(queryset)
        self._count = total_result

        return queryset

    def _get_brands(self, queryset: QuerySet = None):
        """
        Получает уникальные бренды из QuerySet.
        """

        if queryset is None:
            queryset = self.qs

        return queryset.values_list("brand", flat=True).distinct()

    def _get_chars(self, queryset: QuerySet = None):
        """
        Получает доступные характеристики для товаров в QuerySet.
        """

        if queryset is None:
            queryset = self.qs

        result = []
        category_ids = queryset.values_list("category", flat=True)
        characteristics_queryset = Characteristic.objects.filter(
            Q(categories__children__in=category_ids) | Q(categories__in=category_ids),
            for_filtering=True,
            is_active=True,
        ).distinct()
        for char in characteristics_queryset:
            values = (
                char.characteristicvalue_set.filter(
                    product__in=queryset, is_active=True
                )
                .values("value", "slug")
                .order_by("slug")
                .distinct("slug")
            )
            if values.exists():
                result.append({"name": char.name, "slug": char.slug, "values": values})

        return result

    def filter_category(self, queryset, name, value):
        """
        Фильтрует товары по категории и дочерним категориям.
        """

        q = Q()
        category_slugs = set(map(lambda x: x.strip(), value.split(",")))
        for ctg in Category.objects.filter(slug__in=category_slugs):
            category_slugs.update(
                ctg.get_descendants()
                .filter(is_active=True, is_visible=True)
                .values_list("slug", flat=True)
            )

        q |= Q(category__slug__in=category_slugs)
        q |= Q(additional_categories__slug=category_slugs)

        queryset = queryset.filter(q).distinct()
        if not self.data.get("search"):
            self._chars = self._get_chars(queryset)
            self._brands = self._get_brands(queryset)

        return queryset

    def filter_characteristics(self, queryset, name, value):
        """
        Фильтрует товары по значениям характеристик.
        """

        char_slugs = {}
        if value:
            filters = value.split(",")
            for f in filters:
                pair = f.split(":", 1)
                if len(pair) > 1:
                    char_name, char_slug = pair[0], pair[1]
                    char_slugs.setdefault(char_name, [])
                    char_slugs[char_name].append(char_slug)

        for slug, values in char_slugs.items():
            queryset = queryset.filter(
                characteristic_values__characteristic__slug=slug,
                characteristic_values__slug__in=values,
                characteristic_values__characteristic__for_filtering=True,
            )

        return queryset.distinct()
