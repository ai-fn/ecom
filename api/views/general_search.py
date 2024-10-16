from django.db.models import QuerySet

from loguru import logger
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from api.mixins import GeneralSearchMixin, PriceFilterMixin, AnnotateProductMixin, CategoriesWithProductsMixin
from api.serializers import ProductDocumentSerializer
from api.views.price import PRICE_RESPONSE_EXAMPLE


from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter,
)
from elasticsearch import ConnectionError


null_price_example = {key: None for key in PRICE_RESPONSE_EXAMPLE.keys() if key != "id"}

product_document_serializer_example = {
    "id": 2,
    "title": "Dummy Title",
    "article": "Dummy Article",
    "description": "Dummy Description",
    "search_image": "/media/catalog/products/search_images/search_image1.webp",
    "category_slug": "Dummy Category Slug",
    "slug": "Dummy Slug",
    "price": PRICE_RESPONSE_EXAMPLE,
}
product_document_serializer_example_with_null_price = {
    **product_document_serializer_example,
    "price": null_price_example,
}
category_document_serializer_example = {
    "id": 1,
    "name": "Dummy Name",
    "description": "Dummy Description",
    "image": "/media/catalog/products/images/test_image_0SFY9TC.jpg",
    "slug": "Dummy Slug",
}
brand_document_serializer_example = {
    "id": 1,
    "name": "Dummy Name",
    "slug": "Dummy Slug",
    "is_active": True,
}


@extend_schema(
    tags=["Search"],
    summary="Поиск товаров в каталоге",
    description="Поиск товаров в катологе",
    parameters=[
        OpenApiParameter(
            name="q",
            description="Поисковый запрос позволяет отфильтровать результаты по названию, описанию и т. д.",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="city_domain",
            description="Домен для фильтрации цен по городу или региону",
            required=False,
            type=str,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductDocumentSerializer(many=False),
            examples=[
                OpenApiExample(
                    "Пример ответа",
                    value={
                        "products": [
                            product_document_serializer_example,
                            product_document_serializer_example_with_null_price,
                        ],
                        "categories": [
                            category_document_serializer_example,
                        ],
                        "brands": [
                            brand_document_serializer_example,
                        ],
                    },
                )
            ],
        ),
    },
)
class GeneralSearchView(GeneralSearchMixin, APIView, PriceFilterMixin, AnnotateProductMixin, CategoriesWithProductsMixin):
    permission_classes = [AllowAny]
    pagination_class = None

    def get(self, request, *args, **kwargs):
        domain = self.request.query_params.get("city_domain", "")
        query = self.request.query_params.get("q", "")

        try:
            result, _ = self.g_search(query, domain)
        except ConnectionError as e:
            logger.error(str(e))
            return Response(
                {"error": f"Error connecting to elasticsearch: {str(e)}"},
                status=HTTP_503_SERVICE_UNAVAILABLE,
            )

        categorized_results = {index: result[index]["queryset"] for index in result}
        for index in result:
            r_d = result[index]
            serializer = r_d["serializer"]
            queryset = r_d["queryset"]

            func_name = f"_process_{index}"
            func = getattr(self, func_name, None)
            if func and callable(func):
                queryset = func(queryset)

            categorized_results[index] = serializer(queryset, many=True).data

        return Response(categorized_results, status=HTTP_200_OK)
    
    def _process_products(self, queryset):
        queryset = self.annotate_queryset(queryset, fields=["prices"])
        return queryset
