from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.decorators import action

from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse
from api.serializers import OpenGraphMetaSerializer
from shop.models import OpenGraphMeta, Product
from shop.services.metadata_service import MetaDataService


OPEN_GRAPH_META_RESPONSE_EXAMPLE = {
    "title": "Документация",
    "description": "Документация",
    "OpenGraph": {
        "url": "/katalog/dokumentaciya/",
        "siteName": "Кров Маркет",
        "images": [
            {
                "image": "/media/pages/image-70e50210-8678-4b3a-90f9-3626526c11cb_ZnnxbcK.webp",
                "width": 1280,
                "height": 720,
            }
        ],
        "locale": "ru_RU",
        "type": "website",
    },
}


@extend_schema(tags=["Shop"])
@extend_schema_view(
    metadata=extend_schema(
        description="Получение метаданных",
        summary="Получение метаданных",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value=OPEN_GRAPH_META_RESPONSE_EXAMPLE,
            )
        ],
        parameters=[
            OpenApiParameter(
                name="content_type",
                description="Тип объекта",
                default="product",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="city_domain",
                description="Домен города",
                default="moskva.domain.com",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="slug",
                description="Slug объекта",
                required=False,
                type=str,
            ),
        ],
    )
)
class MetadataViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, GenericViewSet):
    queryset = OpenGraphMeta.objects.all()
    permission_classes = [AllowAny]
    serializer_class = OpenGraphMetaSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if domain := self.request.query_params.get("city_domain"):
            context["city_domain"] = domain

        return context

    @method_decorator(cache_page(120 * 60))
    @action(detail=False, methods=["get"])
    def metadata(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        obj_slug = request.query_params.get("slug")
        content_type = request.query_params.get("content_type")

        try:
            meta = MetaDataService.get_obj_by_slug(obj_slug, content_type)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

        try:
            serializer = self.get_serializer(meta, context=context)
            data = serializer.data
        except FileNotFoundError as err:
            return Response({"error": str(err)}, status=HTTP_404_NOT_FOUND)

        return Response(data, status=HTTP_200_OK)
