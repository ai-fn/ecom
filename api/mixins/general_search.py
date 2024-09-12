from typing import Iterable, Dict, Any
from elasticsearch_dsl import Q, Search, connections
from loguru import logger
from django.core.cache import cache

from account.models import City
from shop.documents import (
    BrandDocument,
    CategoryDocument,
    ProductDocument,
)
from shop.models import Category, Price, Product, SearchHistory
from api.serializers import (
    PriceSerializer,
    ProductDocumentSerializer,
    CategoryDocumentSerializer,
    BrandDocumentSerializer,
)


class GeneralSearchMixin:
    def g_search(
        self, query: str, domain: str, exclude_: Iterable[str] = None, page: int = 1, per_page: int = 32
    ) -> Dict[str, Any]:
        if self.request.user.is_authenticated:
            SearchHistory.objects.get_or_create(title=query, user=self.request.user)

        exclude_ = set(exclude_ or [])

        self.indexes = {
            ProductDocument._index._name: "product",
            CategoryDocument._index._name: "category",
            BrandDocument._index._name: "brand",
        }

        for index in exclude_:
            try:
                del self.indexes[index]
            except KeyError:
                logger.info(f"SEARCH: tring to del unexpected index: {index}")

        client = connections.get_connection()
        search = (
            Search(using=client, index=list(self.indexes.keys()))
            .query("multi_match", query=query, fields=["title", "description", "name"])
        )
        from_ = (page - 1) * per_page
        search = search[from_:from_ + per_page]

        response = search.execute()
        city = self.get_city_by_domain(domain)
        categorized_results = self.categorize_results(response, city)
        total_size = response.hits.total.value
        return categorized_results, total_size


    def get_total_size(self) -> int:
        return sum(
            globals()[classname.capitalize()].objects.count()
            for classname in self.indexes.values()
            if classname.capitalize() in globals()
        )

    def get_city_by_domain(self, domain: str) -> City:
        cache_key = f"city_{domain}"
        city = cache.get(cache_key)
        if not city:
            city = (
                City.objects.filter(domain=domain).select_related("city_group").first()
            )
            cache.set(cache_key, city, 3600)
        return city

    def categorize_results(self, response, city) -> Dict[str, Any]:
        categorized_results = {
            "categories": [],
            "products": [],
            "reviews": [],
            "brands": [],
        }

        for hit in response:
            if hit.meta.index == ProductDocument._index._name:
                self.process_product(hit, city, categorized_results)
            elif hit.meta.index == CategoryDocument._index._name:
                self.process_category(hit, categorized_results)
            elif hit.meta.index == BrandDocument._index._name:
                self.process_brand(hit, categorized_results)

        return categorized_results

    def process_product(self, hit, city, categorized_results):
        try:
            queryset = Product.objects.select_related(
                "category", "brand"
            ).prefetch_related("additional_categories")
            if city is not None:
                queryset = queryset.exclude(unavailable_in=city)

            product = queryset.get(id=hit.id)
        except Product.DoesNotExist:
            logger.info(f"Product with hit {hit.id} not found")
            return

        product_data = ProductDocumentSerializer(product).data
        if city:
            price = (
                Price.objects.filter(product=product, city_group__cities=city)
                .select_related("city_group")
                .first()
            )
            if price:
                product_data["price"] = PriceSerializer(price).data
        categorized_results["products"].append(product_data)

    def process_category(self, hit, categorized_results):
        try:
            category = Category.objects.get(id=hit.id)
        except Category.DoesNotExist:
            logger.info(f"Category with hit {hit.id} not found")
            return

        serializer = CategoryDocumentSerializer(category)
        categorized_results["categories"].append(serializer.data)

    def process_brand(self, hit, categorized_results):
        serializer = BrandDocumentSerializer(hit).data
        categorized_results["brands"].append(serializer)
