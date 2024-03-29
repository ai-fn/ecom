from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

from shop.documents import CategoryDocument, ProductDocument, ReviewDocument
from shop.models import Category, Product, City, Price
from api.serializers import (
    CategoryDocumentSerializer,
    ProductDocumentSerializer,
    ReviewDocumentSerializer,
    PriceSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    tags=["Search"],
    summary="Поиск товаров в каталоге",
    description="Поиск товаров в катологе",
    parameters=[
        OpenApiParameter(
            name="q",
            description="Search query to filter results by name, description, reviews, etc.",
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="domain",
            description="Domain to filter prices by city or region",
            required=False,
            type=OpenApiTypes.STR,
        ),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
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
        domain = request.query_params.get("domain", "")

        if query:
            search = search.query(
                "bool",
                should=[
                    Q(
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
                    ),
                    Q("wildcard", name={"value": f"*{query}*"}),
                    Q("wildcard", title={"value": f"*{query}*"}),
                    Q("wildcard", description={"value": f"*{query}*"}),
                    Q("wildcard", review={"value": f"*{query}*"}),
                    Q("wildcard", category__name={"value": f"*{query}*"}),
                    Q("wildcard", brand__name={"value": f"*{query}*"}),
                ],
                minimum_should_match=1,
            )

        response = search.execute()

        if domain:
            city = City.objects.filter(domain=domain).first()
        else:
            city = None

        categorized_results = {
            "categories": [],
            "products": [],
            "reviews": [],
        }

        for hit in response:
            if hit.meta.index == ProductDocument._index._name:
                product = Product.objects.get(id=hit.id)

                if city:
                    price = Price.objects.filter(product=product, city=city).first()
                    if price:
                        product_data = ProductDocumentSerializer(product).data
                        product_data["price"] = PriceSerializer(price).data
                        categorized_results["products"].append(product_data)
                else:
                    product_data = ProductDocumentSerializer(product).data
                    categorized_results["products"].append(product_data)
            elif hit.meta.index == CategoryDocument._index._name:
                category = Category.objects.get(id=hit.id)
                serializer = CategoryDocumentSerializer(category)
                categorized_results["categories"].append(serializer.data)
            elif hit.meta.index == ReviewDocument._index._name:
                serializer = ReviewDocumentSerializer(hit)
                categorized_results["reviews"].append(serializer.data)

        return Response(categorized_results)
