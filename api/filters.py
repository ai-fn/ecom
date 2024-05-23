from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters
from django.db.models import Q, F

from api.mixins import GeneralSearchMixin
from shop.models import Category, Price, Product


class PriceFilter(FilterSet):
    class Meta:
        model = Price
        fields = ["city_group"]


class ProductFilter(GeneralSearchMixin, filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    price_lte = filters.NumberFilter(field_name="prices__price", lookup_expr='lte')
    price_gte = filters.NumberFilter(field_name="prices__price", lookup_expr='gte')
    brand_slug = filters.CharFilter(field_name="brand__slug", lookup_expr='icontains')
    category = filters.CharFilter(method='filter_category')
    characteristics = filters.CharFilter(method='filter_characteristics')
    city_domain = filters.CharFilter(method='filter_city_domain')

    class Meta:
        model = Product
        fields = ['search', 'price_lte', 'price_gte', 'brand_slug', 'category', 'characteristics', 'city_domain']

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
        categories = [value]
        try:
            category_instance = Category.objects.get(slug=value)
        except Category.DoesNotExist:
            category_instance = None

        if category_instance:
            category_childrens = category_instance.get_descendants(include_self=True).values_list("slug", flat=True)
            categories.extend(category_childrens)
        queryset = queryset.filter(Q(category__slug__in=categories) | Q(additional_categories__slug=value))
        return queryset 

    def filter_characteristics(self, queryset, name, value):
        characteristics = value.split(",")
        ch_values = []
        for ch in characteristics:
            pair = ch.split(":")
            if len(pair) > 1:
                ch_values.append(pair[1])
        queryset = queryset.filter(characteristic_values__value__in=ch_values).distinct()
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
            queryset = queryset.filter(price_filter).annotate(city_price=F("prices__price"), old_price=F("prices__old_price")).distinct()
        return queryset
