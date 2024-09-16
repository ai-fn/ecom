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
        page: int = 1,
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
                "queries": (
                    Q("match_phrase", title=query),
                    Q("match_phrase", description=query),
                    Q("wildcard", title=f"*{query}*"),
                    Q("wildcard", description=f"*{query}*"),
                    Q("term", article=query),
                ),
            },
            CategoryDocument._index._name: {
                "model": CategoryDocument.Django.model,
                "serializer": CategoryDocumentSerializer,
                "queries": (
                    Q("wildcard", name=f"*{query}*"),
                    Q("match_phrase", name=query),
                ),
            },
            BrandDocument._index._name: {
                "model": BrandDocument.Django.model,
                "serializer": BrandDocumentSerializer,
                "queries": (
                    Q("wildcard", name=f"*{query}*"),
                    Q("match_phrase", name=query),
                ),
            },
        }

        for index in exclude_:
            try:
                del indexes[index]
            except KeyError:
                logger.info(f"SEARCH: tring to del unexpected index: {index}")

        client = connections.get_connection()
        search = Search(using=client)

        for index in indexes.values():
            shoulds.extend(index["queries"])

        queries = Q("bool", should=shoulds)

        search = search.query(queries)
        search = search.filter("term", is_active=True)

        if ordering is not None:
            search = self.sort_config(search, ordering)

        from_ = (page - 1) * per_page
        search = search[from_ : from_ + per_page]

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

        context = {"city_domain": domain}
        for index_name in hits:
            self.process_index(
                indexes,
                index_name,
                hits[index_name],
                categorized_results,
                context=context,
            )

        return categorized_results

    def process_index(self, indexes, index, hits, categorized_results, context):
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
            "serialized": serializer(queryset, context=context, many=True).data,
        }
