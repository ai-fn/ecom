from django.db.models import Case, IntegerField, When, Value
from typing import Iterable, Dict, Any
from elasticsearch_dsl import Search, connections, Q
from loguru import logger
from django.core.cache import cache

from shop.documents import (
    BrandDocument,
    CategoryDocument,
    ProductDocument,
)
from shop.models import SearchHistory
from api.serializers import (
    ProductDocumentSerializer,
    CategoryDocumentSerializer,
    BrandDocumentSerializer,
)


class GeneralSearchMixin:
    def g_search(
        self,
        query: str,
        domain: str,
        exclude_: Iterable[str] = None,
        page: int = None,
        per_page: int = 32,
        ordering: str = None,
    ) -> Dict[str, Any]:
        if self.request.user.is_authenticated:
            SearchHistory.objects.get_or_create(title=query, user=self.request.user)

        shoulds = []
        exclude_ = set(exclude_ or [])
        query = query.lower()

        indexes = {
            ProductDocument._index._name: {
                "model": ProductDocument.Django.model,
                "serializer": ProductDocumentSerializer,
                "queries": Q(
                    # "match_all",
                    "bool",
                    must=[
                        Q("match", prices__cg_domain=domain),
                        Q("term", _index=ProductDocument._index._name),
                    ],
                    should=(
                        Q("term", article={"value": query, "boost": 5.0}),
                        Q("fuzzy", title={"value": query, "fuzziness": "AUTO", "boost": 5.0}),
                        Q("wildcard", title={"value": f"*{query}*", "boost": 2.5}),
                        Q("wildcard", description={"value": f"*{query}*", "boost": 1.5}),
                        Q("match_phrase", title=query),
                        Q("match_phrase", description=query),
                    ),
                    minimum_should_match=1,
                ),
            },
            CategoryDocument._index._name: {
                "model": CategoryDocument.Django.model,
                "serializer": CategoryDocumentSerializer,
                "queries": Q(
                    "bool",
                    must=[
                        Q("term", is_visible=True),
                        Q("term", products_exist=True),
                        Q("term", _index=CategoryDocument._index._name),
                    ],
                    should=(
                        Q("term", name={"value": query, "boost": 4.0}),
                        Q("fuzzy", name={"value": query, "fuzziness": "AUTO", "boost": 4.0}),
                        Q("wildcard", name={"value": f"*{query}*", "boost": 2.7}),
                        Q("match", name=query),
                        Q("match_phrase", name=query),
                    ),
                    minimum_should_match=1,
                ),
            },
            BrandDocument._index._name: {
                "model": BrandDocument.Django.model,
                "serializer": BrandDocumentSerializer,
                "queries": Q(
                    "bool",
                    must=[Q("term", _index=BrandDocument._index._name)],
                    should=[
                        Q("term", name={"value": query, "boost": 3.0}),
                        Q("fuzzy", name={"value": query, "fuzziness": "AUTO", "boost": 3.0}),
                        Q("wildcard", name={"value": f"*{query}*", "boost": 2.6}),
                        Q("match_phrase", name=query),
                    ],
                    minimum_should_match=1,
                ),
            },
        }

        for index in exclude_:
            try:
                del indexes[index]
            except KeyError:
                logger.info(f"SEARCH: trying to del unexpected index: {index}")

        client = connections.get_connection()
        search = Search(using=client)

        for index in indexes.values():
            shoulds.append(index["queries"])

        queries = Q("bool", should=shoulds)

        search = search.query(queries)
        search = search.filter("term", is_active=True)

        if ordering is not None:
            search = self.sort_config(search, ordering)

        if page is not None:
            from_ = (page - 1) * per_page
            search = search[from_ : from_ + per_page]
        else:
            search = search.extra(size=10)

        response = search.execute()

        categorized_results = self.categorize_results(response, indexes, domain)
        total_size = response.hits.total.value
        return categorized_results, total_size

    def sort_config(self, search, ordering):
        if ordering.startswith("-"):
            sort_order = "desc"
            ordering = ordering[1:]
        else:
            sort_order = "asc"

        sort_args = {"order": sort_order}
        if "in_promo" in ordering:
            ordering = "price.in_promo"
        elif "price" in ordering:
            ordering = "price.price"
            sort_args["nested"] = {"path": "price"}

        return search.sort(
            {ordering: sort_args},
            {"_score": {"order": "desc"}},
            {"priority": {"order": "desc"}},
        )

    def categorize_results(self, response, indexes, domain) -> Dict[str, Any]:
        categorized_results = dict()
        hits = {index_name: list() for index_name in indexes}

        for hit in response:
            if hit.meta.index in hits:
                hits[hit.meta.index].append(hit)

        for index_name in hits:
            self.process_index(
                indexes,
                index_name,
                hits[index_name],
                categorized_results,
            )

        return categorized_results

    def process_index(self, indexes, index, hits, categorized_results):
        ids = [hit.id for hit in hits]
        model = indexes[index]["model"]
        serializer = indexes[index]["serializer"]
        queryset = (
            model.objects.filter(pk__in=ids)
            .annotate(
                score_order=Case(
                    *[When(pk=id, then=Value(idx)) for idx, id in enumerate(ids)],
                    output_field=IntegerField(),
                )
            )
            .order_by("score_order")
        )

        categorized_results[index] = {
            "queryset": queryset,
            "serializer": serializer,
        }
