from django.utils.functional import cached_property
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
    characteristics = filters.CharFilter(
        method='filter_characteristics',
        label="Значения характеристик"
    )
    city_domain = filters.CharFilter(method='filter_city_domain')

    # @cached_property
    # def qs(self):
    #     session = self.request.session

    #     if not any(param in self.request.query_params for param in self.Meta.fields):
    #         if "filtered_products" in session:
    #             print("deleting filtered products from session...")
    #             del self.request.session["filtered_products"]
    #         return Product.objects.all()
    #     else:
    #         if 'filtered_products' in session:
    #             print("return filtered products from session...")
    #             initial_queryset = Product.objects.filter(pk__in=session['filtered_products'])
    #         else:
    #             print("return all products...")
    #             initial_queryset = Product.objects.all()
            
    #         return self.filter_queryset(initial_queryset)


    # def get_queryset(self):
    #     session = self.request.session
    #     if 'filtered_products' in session:
    #         initial_queryset = Product.objects.filter(pk__in=session['filtered_products'])
    #     else:
    #         initial_queryset = Product.objects.all()

    #     # Сохранение начального списка продуктов в сессии
    #     session['filtered_products'] = list(initial_queryset.values_list('pk', flat=True))
    #     session.modified = True

    #     return initial_queryset


    class Meta:
        model = Product
        fields = ['search', 'category', 'brand_slug', 'price_lte', 'price_gte', 'characteristics', 'city_domain']


    # def filter_search(self, queryset, name, value):
    #     return self.apply_filter(queryset, self._filter_search, name, value)

    # def filter_category(self, queryset, name, value):
    #     return self.apply_filter(queryset, self._filter_category, name, value)

    # def filter_characteristics(self, queryset, name, value):
    #     return self.apply_filter(queryset, self._filter_characteristics, name, value)

    # def filter_city_domain(self, queryset, name, value):
    #     return self.apply_filter(queryset, self._filter_city_domain, name, value)

    # def apply_filter(self, queryset, filter_func, name, value):
    #     """Общий метод для применения фильтра и обновления сессии."""
    #     queryset = self.get_queryset()
    #     queryset = filter_func(queryset, name, value)
    #     self.request.session['filtered_products'] = list(queryset.values_list('pk', flat=True))
    #     self.request.session.modified = True
    #     return queryset

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
        char_slugs = {}
        filter_conditions = Q()
        if value:
            filters = value.split(',')
            for f in filters:
                pair = f.split(':', 1)
                if len(pair) > 1:
                    char_name, char_slug = pair[0], pair[1]
                    char_slugs.setdefault(char_name, [])
                    char_slugs[char_name].append(char_slug)

        for char in char_slugs:
            filter_conditions &= Q(characteristic_values__characteristic__slug=char, characteristic_values__slug__in=char_slugs[char])
        
        queryset = queryset.filter(filter_conditions, characteristic_values__characteristic__for_filtering=True).distinct()
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
