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
        200: OpenApiTypes.OBJECT,  # Укажите здесь более конкретные типы, если это необходимо
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
            search = search.query(
                "bool",
                should=[
                    Q("fuzzy", name={"value": query, "fuzziness": 2}),
                    Q("fuzzy", title={"value": query, "fuzziness": 2}),
                    Q("fuzzy", description={"value": query, "fuzziness": 2}),
                    Q("fuzzy", review={"value": query, "fuzziness": 2}),
                    Q("fuzzy", category__name={"value": query, "fuzziness": 2}),
                    Q("fuzzy", brand__name={"value": query, "fuzziness": 2}),
                ],
                minimum_should_match=1,
            )

        response = search.execute()

        # Collect IDs for batch queries
        category_ids = []
        product_ids = []
        review_hits = []  # Assuming Review documents contain all necessary info
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
