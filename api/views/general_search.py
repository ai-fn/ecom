from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from drf_spectacular.utils import OpenApiExample

from shop.documents import CategoryDocument, ProductDocument, ReviewDocument
from api.serializers import (
    CategoryDocumentSerializer,
    ProductDocumentSerializer,
    ReviewDocumentSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from shop.models import Category, Product

@extend_schema(
    parameters=[
        OpenApiParameter(
            name="q",
            description="Search query to filter results by name, description, reviews, etc.",
            required=False,
            type=OpenApiTypes.STR,
            examples=[
                OpenApiExample(
                    "Example search",
                    summary="Simple example",
                    description='Example of a search query, for instance, "tv"',
                    value="tv",
                ),
            ],
        )
    ],
    responses={
        200: OpenApiTypes.OBJECT,  # Specify more specific types here if necessary
    },
)
class GeneralSearchView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        client = connections.get_connection()
        search = Search(
            using=client,
            index=[
                CategoryDocument._index._name,
                ProductDocument._index._name,
                ReviewDocument._index._name,
            ],
        )

        query = request.query_params.get("q", "")
        if query:
            # Enhancing flexibility by combining multi-match for broader search across fields,
            # wildcard for partial matches, and boosting fields to prioritize their relevance.
            multi_match_query = Q("multi_match", query=query, fields=[
                'name^3',  # Boost name field
                'title^2',  # Boost title field
                'description',
                'review',
                'category__name',
                'brand__name'
            ], type='best_fields')

            wildcard_query = Q("bool", should=[
                Q("wildcard", name={"value": f"*{query}*"}),
                Q("wildcard", title={"value": f"*{query}*"}),
                Q("wildcard", description={"value": f"*{query}*"}),
                Q("wildcard", review={"value": f"*{query}*"}),
                Q("wildcard", category__name={"value": f"*{query}*"}),
                Q("wildcard", brand__name={"value": f"*{query}*"})
            ], minimum_should_match=1)

            search = search.query(
                "bool",
                should=[multi_match_query, wildcard_query],
                minimum_should_match=1
            )

        response = search.execute()

        # Collect IDs for batch queries
        category_ids = []
        product_ids = []
        review_hits = []
        for hit in response:
            if hit.meta.index == CategoryDocument._index._name:
                category_ids.append(hit.id)
            elif hit.meta.index == ProductDocument._index._name:
                product_ids.append(hit.id)
            elif hit.meta.index == ReviewDocument._index._name:
                review_hits.append(hit)

        # Perform batch queries
        categories = {c.id: c for c in Category.objects.filter(id__in=category_ids)}
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        # Serialize and collect results
        results = []
        for hit in response:
            if hit.meta.index == CategoryDocument._index._name:
                serializer = CategoryDocumentSerializer(categories.get(hit.id))
                results.append(serializer.data)
            elif hit.meta.index == ProductDocument._index._name:
                serializer = ProductDocumentSerializer(products.get(hit.id))
                results.append(serializer.data)
            elif hit.meta.index == ReviewDocument._index._name:
                serializer = ReviewDocumentSerializer(hit)
                results.append(serializer.data)

        return Response({"results": results})
