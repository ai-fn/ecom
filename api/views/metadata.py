from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, OpenApiParameter


from shop.models import OpenGraphMeta


@extend_schema(
    tags=["Shop"]
)
class MetadataApiView(GenericViewSet):
    queryset = OpenGraphMeta.objects.all()
    permission_classes = [AllowAny]

    @extend_schema(
        description="Получение метаданных",
        summary="Получение метаданных",
        parameters=[
            OpenApiParameter(
                name="page_type",
                description="Тип страницы",
                default="product",
                required=True,
            ),
            OpenApiParameter(
                name="city_domain",
                description="Домен города",
                default="moskva.krov.market",
                required=True,
            ),
            OpenApiParameter(
                name="slug",
                description="Slug товара или категории",
                required=False,
            ),
        ]
    )
    @action(detail=False, methods=["get"])
    def get_metadata(self, request, *args, **kwargs):
        return Response()

    def _get_product_metadata(self):
        pass
