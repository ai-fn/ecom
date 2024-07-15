from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework import generics, permissions, response, status
from api.mixins import CityPricesMixin
from api.serializers import ProductCatalogSerializer
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter


@extend_schema(tags=["Shop"])
class SimilarProducts(CityPricesMixin, ListModelMixin, GenericViewSet):

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
                            "name": "updated_example",
                            "thumb_img": "thumb_example_updated.png",
                            "image": "/media/catalog/products/images/example_updated.png",
                            "is_active": True,
                        },
                        {
                            "id": 1,
                            "name": "updated_example",
                            "thumb_img": "thumb_example_updated.png",
                            "image": "/media/catalog/products/images/example_updated.png",
                            "is_active": True,
                        },
                    ],
                    "category_slug": "category-a",
                },
            )
        ],
    )
    def get(self, request, product_id, **kwargs):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist as err:
            return response.Response(
                {"error": str(err)}, status=status.HTTP_400_BAD_REQUEST
            )

        self.domain = request.query_params.get("city_domain")
        self.queryset = self.filter_queryset(product.similar_products.all())
        if self.domain:
            self.queryset = self.queryset.exclude(
                unavailable_in__domain=self.domain
            )

        return super().list(request, **kwargs)
