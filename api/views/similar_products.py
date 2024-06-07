from rest_framework import generics, permissions, response, status
from api.mixins import CityPricesMixin
from api.serializers import ProductCatalogSerializer
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter


@extend_schema(tags=["Shop"])
class SimilarProducts(CityPricesMixin, generics.GenericAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    queryset = Product.objects.all()

    @extend_schema(
        description="Получить список всех похожих продуктов",
        summary="Получить список всех похожих продуктов",
        responses={200: ProductCatalogSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для фильтрации цен",
            ),
        ],
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "title": "Product A",
                    "brand": 1,
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "id": 1,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                },
            )
        ],
    )
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist as err:
            return response.Response(
                {"error": str(err)}, status=status.HTTP_400_BAD_REQUEST
            )

        self.domain = request.query_params.get("city_domain")
        queryset = product.similar_products.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return response.Response(serializer.data, status=status.HTTP_200_OK)
