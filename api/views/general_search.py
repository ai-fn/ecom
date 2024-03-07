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
            multi_match_query = Q(
                "multi_match",
                query=query,
                fields=[
                    "name^3",
                    "title^2",
                    "description",
                    "review",
                    "category__name",
                    "brand__name",
                ],
                type="best_fields",
            )

            wildcard_query = Q(
                "bool",
                should=[
                    Q("wildcard", name={"value": f"*{query}*"}),
                    Q("wildcard", title={"value": f"*{query}*"}),
                    Q("wildcard", description={"value": f"*{query}*"}),
                    Q("wildcard", review={"value": f"*{query}*"}),
                    Q("wildcard", category__name={"value": f"*{query}*"}),
                    Q("wildcard", brand__name={"value": f"*{query}*"}),
                ],
                minimum_should_match=1,
            )

            search = search.query(
                "bool",
                should=[multi_match_query, wildcard_query],
                minimum_should_match=1,
            )

        response = search.execute()

        # Initialize dictionaries for each category of results
        categorized_results = {
            "categories": [],
            "products": [],
            "reviews": [],
        }

        # Perform batch queries and serialization
        category_ids = [
            hit.id
            for hit in response
            if hit.meta.index == CategoryDocument._index._name
        ]
        product_ids = [
            hit.id for hit in response if hit.meta.index == ProductDocument._index._name
        ]
        categories = {c.id: c for c in Category.objects.filter(id__in=category_ids)}
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        for hit in response:
            if hit.meta.index == CategoryDocument._index._name:
                serializer = CategoryDocumentSerializer(categories.get(hit.id))
                categorized_results["categories"].append(serializer.data)
            elif hit.meta.index == ProductDocument._index._name:
                serializer = ProductDocumentSerializer(products.get(hit.id))
                categorized_results["products"].append(serializer.data)
            elif hit.meta.index == ReviewDocument._index._name:
                serializer = ReviewDocumentSerializer(hit)
                categorized_results["reviews"].append(serializer.data)

        return Response(categorized_results)
