from rest_framework import status, permissions, generics, views
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from api.serializers import ProductCatalogSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample
from shop.models import Product


@extend_schema(tags=["Shop"])
class ProductsById(generics.GenericAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    pagination_class = PageNumberPagination

    @extend_schema(
        description="Получение информации о товарах по массиву с id товаров",
        summary="Получение информации о товарах по массиву с id товаров",
        examples=[
            OpenApiExample(
                name="Request Products Example",
                value={
                    "ids_list": [
                        5572,
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Response Products Example",
                value=[
                    {
                        "id": 5572,
                        "title": "Чердачная лестница Standard Metal",
                        "brand": 1,
                        "image": "http://dev-api-shop.altawest.ru/media/catalog/products/ee08e97e-45be-4415-ab4e-f3f9133cf307.webp&...",
                        "slug": "cherdachnaia-lestnitsa-standard-metal-5572",
                        "old_price": 120.0,
                        "new_price": 150.0,
                        "images": [
                            {
                                "image_url": "http://dev-api-shop.altawest.ru/media/catalog/products/ee08e97e-45be-4415-ab4e-f3f9133cf307.webp&...;",
                            }
                        ],
                        "category_slug": "deke",
                    },
                ],
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        ids_list = request.data.get("ids_list")
        if not ids_list:
            return Response(
                {"error": "ID's list is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = Product.objects.filter(id__in=ids_list)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
