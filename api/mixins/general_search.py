from typing import Iterable
from elasticsearch_dsl import Q, Search, connections
from loguru import logger

from account.models import City
from shop.documents import (
    BrandDocument,
    CategoryDocument,
    ProductDocument,
    ReviewDocument,
)
from shop.models import Category, Price, Product, SearchHistory
from api.serializers import (
    PriceSerializer,
    ReviewDocumentSerializer,
    ProductDocumentSerializer,
    CategoryDocumentSerializer,
    BrandDocumentSerializer,
)


class GeneralSearchMixin:

    def g_search(self, query: str, domain: str, exclude_: Iterable = None):

        if self.request.user.is_authenticated:
            SearchHistory.objects.get_or_create(title=query, user=self.request.user)

        exclude_ = exclude_ or []
        default = {
            "product": {
                "queries": (
                    Q("wildcard", title={"value": f"*{query}*"}),
                    Q("wildcard", description={"value": f"*{query}*"}),
                ),
                "fields": ("title^2", "description"),
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

        should, fields, indexes = [], [], []

        for key, config in default.items():
            if key not in exclude_:
                should.extend(config.get("queries", []))
                fields.extend(config.get("fields", []))
                indexes.extend(config.get("indexes", []))

        client = connections.get_connection()
        search = Search(using=client, index=indexes)

        if exclude_:
            search = search.extra(
                size=sum(
                    [
                        globals()[classname.capitalize()].objects.count()
                        for classname in default
                        if classname not in exclude_
                        and classname.capitalize() in globals()
                    ]
                )
            )

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

        city = City.objects.filter(domain=domain).first() if domain else None
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
            elif hit.meta.index == ReviewDocument._index._name:
                self.process_review(hit, categorized_results)
            elif hit.meta.index == BrandDocument._index._name:
                self.process_brand(hit, categorized_results)

        return categorized_results

    def process_product(self, hit, city, categorized_results):
        try:
            product = Product.objects.exclude(unavailable_in=city).get(id=hit.id)
        except Product.DoesNotExist:
            logger.info(f"Product with hit {hit.id} not found")
            return

        product_data = ProductDocumentSerializer(product).data
        if city:
            price = Price.objects.filter(
                product=product, city_group__cities=city
            ).first()
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
