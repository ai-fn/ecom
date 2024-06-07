from django.db.models import F

from rest_framework.generics import GenericAPIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from api.serializers import ProductCatalogSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from shop.models import Product
from api.mixins import CityPricesMixin


@extend_schema(tags=["Shop"])
class ProductsById(CityPricesMixin, GenericAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    pagination_class = PageNumberPagination
    queryset = Product.objects.all()

    @extend_schema(
        description="Получение информации о товарах по массиву с id товаров",
        summary="Получение информации о товарах по массиву с id товаров",
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для получения цены товара",
            )
        ],
        examples=[
            OpenApiExample(
                name="Request Products Example",
                value={
                    "ids_list": [
                        5572,
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Domain Provided Example",
                value={
                    "id": 5572,
                    "title": "Чердачная лестница Standard Metal",
                    "brand": 1,
                    "image": "http://dev-api-shop.altawest.rucatalog/products/ee08e97e-45be-4415-ab4e-f3f9133cf307.webp&...",
                    "slug": "cherdachnaia-lestnitsa-standard-metal-5572",
                    "city_price": "6865",
                    "old_price": "3865",
                    "images": [
                        {
                            "image_url": "http://dev-api-shop.altawest.rucatalog/products/ee08e97e-45be-4415-ab4e-f3f9133cf307.webp&...;",
                        }
                    ],
                    "category_slug": "deke",
                    "in_stock": True,
                    "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Domain Not Provided Example",
                value={
                    "id": 5572,
                    "title": "Чердачная лестница Standard Metal",
                    "brand": 1,
                    "image": "http://dev-api-shop.altawest.rucatalog/products/ee08e97e-45be-4415-ab4e-f3f9133cf307.webp&...",
                    "slug": "cherdachnaia-lestnitsa-standard-metal-5572",
                    "images": [
                        {
                            "image_url": "http://dev-api-shop.altawest.rucatalog/products/ee08e97e-45be-4415-ab4e-f3f9133cf307.webp&...;",
                        }
                    ],
                    "category_slug": "deke",
                    "in_stock": True,
                    "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        self.domain = request.query_params.get("city_domain")
        ids_list = request.data.get("ids_list")

        if not ids_list:
            return Response(
                {"error": "ID's list is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        self.queryset = self.queryset.filter(pk__in=ids_list)

        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
