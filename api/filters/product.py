from django_filters import rest_framework as filters
from django.db.models import Q, F, Min, Max

from api.mixins import GeneralSearchMixin
from shop.models import Category, Product


class CustomFilter(filters.FilterSet):

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None, city_domain: str = None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.city_domain = city_domain


class ProductFilter(GeneralSearchMixin, CustomFilter):
    search = filters.CharFilter(method="filter_search")
    price_lte = filters.NumberFilter(field_name="prices__price", lookup_expr="lte")
    price_gte = filters.NumberFilter(field_name="prices__price", lookup_expr="gte")
    brand_slug = filters.CharFilter(field_name="brand__slug", lookup_expr="icontains")
    category = filters.CharFilter(method="filter_category")
    characteristics = filters.CharFilter(
        method="filter_characteristics", label="Значения характеристик"
    )

    class Meta:
        model = Product
        fields = [
            "search",
            "category",
            "brand_slug",
            "price_lte",
            "price_gte",
            "characteristics",
        ]

    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            if name not in ["price_lte", "price_gte"] and value is not None:
                queryset = self.filters[name].filter(queryset, value)

        aggregates = queryset.aggregate(
            min_price=Min("prices__price"), max_price=Max("prices__price")
        )
        self.min_price = aggregates["min_price"]
        self.max_price = aggregates["max_price"]


        queryset = self.apply_price_filters(queryset)

        return queryset

    def apply_price_filters(self, queryset):
        gte_data = self.data.get("price_gte")
        lte_data = self.data.get("price_lte")

        if lte_data is not None:
            queryset = queryset.filter(prices__price__lte=lte_data, prices__city_group__cities__domain=self.city_domain)
        if gte_data is not None:
            queryset = queryset.filter(prices__price__gte=gte_data, prices__city_group__cities__domain=self.city_domain)

        return queryset

    def filter_search(self, queryset, name, value):
        domain = self.request.query_params.get("city_domain")
        search_results = self.g_search(
            value, domain, exclude_=("review", "brand", "category")
        )["products"]
        if search_results:
            queryset = queryset.filter(
                pk__in=[el.get("id", 0) for el in search_results]
            )
        else:
            queryset = Product.objects.none()
        return queryset

    def filter_category(self, queryset, name, value):
        q = Q()
        category_slugs = set(map(lambda x: x.strip(), value.split(",")))
        ctgs = Category.objects.filter(
            is_active=True,
            is_visible=True,
            slug__in=category_slugs,
        )
        for ctg in ctgs:

            q |= Q(category=ctg)
            q |= Q(additional_categories=ctg)
            q |= Q(
                category__in=ctg.get_descendants().filter(
                    is_active=True, is_visible=True
                )
            )

        queryset = queryset.filter(q).distinct()
        return queryset

    def filter_characteristics(self, queryset, name, value):
        char_slugs = {}
        filter_conditions = Q()
        if value:
            filters = value.split(",")
            for f in filters:
                pair = f.split(":", 1)
                if len(pair) > 1:
                    char_name, char_slug = pair[0], pair[1]
                    char_slugs.setdefault(char_name, [])
                    char_slugs[char_name].append(char_slug)

        for char in char_slugs:
            filter_conditions &= Q(
                characteristic_values__characteristic__slug=char,
                characteristic_values__slug__in=char_slugs[char],
                characteristic_values__characteristic__for_filtering=True,
            )

        queryset = queryset.filter(filter_conditions).distinct()
        return queryset
