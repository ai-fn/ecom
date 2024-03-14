from rest_framework import generics, permissions, response, status
from api.serializers import ProductCatalogSerializer
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=['Shop']
)
class SimilarProducts(generics.GenericAPIView):
    
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    queryset = Product.objects.all()

    @extend_schema(
        description="Получить список всех похожих продуктов",
        summary="Получить список всех похожих продуктов",
        responses={200: ProductCatalogSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "title": "Product A",
                        "brand": 1,
                        "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "slug": "product-a",
                        "city_price": 100.0,
                        "old_price": 120.0,
                        "images": [
                            {
                                "id": 1,
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "id": 2,
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-a",
                    },
                    {
                        "id": 2,
                        "title": "Product B",
                        "brand": 2,
                        "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "slug": "product-b",
                        "city_price": 150.0,
                        "old_price": 110.0,
                        "images": [
                            {
                                "id": 1,
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "id": 2,
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-b",
                    },
                ],
            )
        ],
    )
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist as err:
            return response.Response({'error': str(err)}, status=status.HTTP_400_BAD_REQUEST)
        
        serialized_products = self.serializer_class(product.similar_products, many=True).data
        return response.Response({'similar_products': serialized_products}, status=status.HTTP_200_OK)
