from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework import permissions, response, status
from api.serializers import ProductCatalogSerializer
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE


@extend_schema(tags=["Shop"])
class SimilarProducts(ListModelMixin, GenericViewSet):

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductCatalogSerializer
    queryset = Product.objects.order_by("-priority")

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
                value=UNAUTHORIZED_RESPONSE_EXAMPLE,
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
