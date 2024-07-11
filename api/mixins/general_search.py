from typing import Iterable, Dict, Any
from elasticsearch_dsl import Q, Search, connections
from loguru import logger
from django.core.cache import cache

from account.models import City
from shop.documents import BrandDocument, CategoryDocument, ProductDocument, ReviewDocument
from shop.models import Category, Price, Product, SearchHistory
from api.serializers import PriceSerializer, ReviewDocumentSerializer, ProductDocumentSerializer, CategoryDocumentSerializer, BrandDocumentSerializer


class GeneralSearchMixin:
    def g_search(self, query: str, domain: str, exclude_: Iterable[str] = None) -> Dict[str, Any]:
        if self.request.user.is_authenticated:
            SearchHistory.objects.get_or_create(title=query, user=self.request.user)

        exclude_ = set(exclude_ or [])
        search_configs = self.get_search_configs(query)

        should, fields, indexes = [], [], []
        for key, config in search_configs.items():
            if key not in exclude_:
                should.extend(config["queries"])
                fields.extend(config["fields"])
                indexes.extend(config["indexes"])

        client = connections.get_connection()
        search = Search(using=client, index=indexes)

        if exclude_:
            search = search.extra(size=self.get_total_size(search_configs, exclude_))

        if query:
            search = search.query(
                "bool",
                should=[
                    Q("multi_match", query=query, fields=["name^3", *fields]),
                    Q("wildcard", name={"value": f"*{query}*"}),
                    *should,
                ],
                minimum_should_match=1,
            )

        response = search.execute()
        city = self.get_city_by_domain(domain)
        categorized_results = self.categorize_results(response, city)

        return categorized_results

    def get_search_configs(self, query: str) -> Dict[str, Dict[str, Any]]:
        return {
            "product": {
                "queries": (
                    Q("wildcard", title={"value": f"*{query}*"}),
                    Q("wildcard", description={"value": f"*{query}*"}),
                    Q("term", article={"value": query}),
                ),
                "fields": ("title^2", "description", "article"),
                "indexes": (ProductDocument._index._name,),
            },
            "category": {
                "queries": (Q("wildcard", category__name={"value": f"*{query}*"}),),
                "fields": ("category__name",),
                "indexes": (CategoryDocument._index._name,),
            },
            "brand": {
                "queries": (Q("wildcard", brand__name={"value": f"*{query}*"}),),
                "fields": ("brand__name",),
                "indexes": (BrandDocument._index._name,),
            },
            "review": {
                "queries": (Q("wildcard", review={"value": f"*{query}*"}),),
                "fields": ("review",),
                "indexes": (ReviewDocument._index._name,),
            },
        }

    def get_total_size(self, search_configs: Dict[str, Dict[str, Any]], exclude_: Iterable[str]) -> int:
        return sum(
            globals()[classname.capitalize()].objects.count()
            for classname in search_configs
            if classname not in exclude_ and classname.capitalize() in globals()
        )

    def get_city_by_domain(self, domain: str) -> City:
        cache_key = f"city_{domain}"
        city = cache.get(cache_key)
        if not city:
            city = City.objects.filter(domain=domain).select_related('city_group').first()
            cache.set(cache_key, city, 3600)
        return city

    def categorize_results(self, response, city) -> Dict[str, Any]:
        categorized_results = {"categories": [], "products": [], "reviews": [], "brands": []}

        for hit in response:
            if hit.meta.index == ProductDocument._index._name:
                self.process_product(hit, city, categorized_results)
            elif hit.meta.index == CategoryDocument._index._name:
                self.process_category(hit, categorized_results)
            elif hit.meta.index == ReviewDocument._index._name:
                self.process_review(hit, categorized_results)
            elif hit.meta.index == BrandDocument._index._name:
                self.process_brand(hit, categorized_results)

        return categorized_results

    def process_product(self, hit, city, categorized_results):
        try:
            product = Product.objects.select_related('category', 'brand').prefetch_related('additional_categories').exclude(unavailable_in=city).get(id=hit.id)
        except Product.DoesNotExist:
            logger.info(f"Product with hit {hit.id} not found")
            return

        product_data = ProductDocumentSerializer(product).data
        if city:
            price = Price.objects.filter(product=product, city_group__cities=city).select_related('city_group').first()
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

    def process_review(self, hit, categorized_results):
        serializer = ReviewDocumentSerializer(hit).data
        categorized_results["reviews"].append(serializer)

    def process_brand(self, hit, categorized_results):
        serializer = BrandDocumentSerializer(hit).data
        categorized_results["brands"].append(serializer)
