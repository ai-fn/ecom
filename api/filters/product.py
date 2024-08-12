from django_filters import rest_framework as filters
from django.db.models import Q, F
from loguru import logger

from api.mixins import GeneralSearchMixin
from shop.models import Category, Product


class ProductFilter(GeneralSearchMixin, filters.FilterSet):
    search = filters.CharFilter(method="filter_search")
    price_lte = filters.NumberFilter(field_name="prices__price", lookup_expr="lte")
    price_gte = filters.NumberFilter(field_name="prices__price", lookup_expr="gte")
    brand_slug = filters.CharFilter(field_name="brand__slug", lookup_expr="icontains")
    category = filters.CharFilter(method="filter_category")
    characteristics = filters.CharFilter(
        method="filter_characteristics", label="Значения характеристик"
    )
    city_domain = filters.CharFilter(method="filter_city_domain")

    class Meta:
        model = Product
        fields = [
            "search",
            "category",
            "brand_slug",
            "price_lte",
            "price_gte",
            "characteristics",
            "city_domain",
        ]

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
        category_slugs = set(map(lambda x: x.strip(), value.split(",")))

        queryset = queryset.filter(
            (
                Q(
                    category__is_active=True,
                    category__is_visible=True,
                    category__slug__in=category_slugs,
                )
                | Q(
                    category__is_active=True,
                    category__is_visible=True,
                    category__children__is_active=True,
                    category__children__is_visible=True,
                    category__children__slug__in=category_slugs,
                )
                | Q(
                    additional_categories__is_active=True,
                    additional_categories__is_visible=True,
                    additional_categories__slug__in=category_slugs,
                )
                | Q(
                    additional_categories__is_active=True,
                    additional_categories__is_visible=True,
                    additional_categories__children__is_visible=True,
                    additional_categories__children__is_active=True,
                    additional_categories__children__slug__in=category_slugs,
                )
            )
        ).distinct()
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

    def filter_city_domain(self, queryset, name, value):
        price_gte = self.request.query_params.get("price_gte")
        price_lte = self.request.query_params.get("price_lte")
        if value and (price_gte or price_lte):
            price_filter = Q(prices__city_group__cities__domain=value)
            if price_lte:
                price_filter &= Q(prices__price__lte=price_lte)
            if price_gte:
                price_filter &= Q(prices__price__gte=price_gte)
            queryset = (
                queryset.filter(price_filter)
                .annotate(
                    city_price=F("prices__price"), old_price=F("prices__old_price")
                )
                .distinct()
            )
        return queryset
