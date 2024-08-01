from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.decorators import action

from django.utils.translation import gettext_lazy as _

from PIL import Image
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


from api.serializers import OpenGraphMetaSerializer
from shop.models import OpenGraphMeta, Product
from shop.services.metadata_service import MetaDataService


@extend_schema(tags=["Shop"])
class MetadataViewSet(GenericViewSet):
    queryset = OpenGraphMeta.objects.all()
    permission_classes = [AllowAny]
    serializer_class = OpenGraphMetaSerializer

    @extend_schema(
        description="Получение метаданных",
        summary="Получение метаданных",
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value={
                    "title": "Документация",
                    "description": "Документация",
                    "OpenGraph": {
                        "url": "http://moskva.krov.market/dokumentaciya/",
                        "siteName": "Кров маркет",
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
                },
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
                default="moskva.krov.market",
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
    @action(detail=False, methods=["get"])
    def metadata(self, request, *args, **kwargs):
        content_type = request.query_params.get("content_type")
        obj_slug = request.query_params.get("slug")
        context = self.get_serializer_context()

        try:
            if content_type == "product":
                prod = Product.objects.get(slug=obj_slug)
                obj_slug = prod.category.slug
                content_type = prod.category._meta.model_name
                context["instance"] = prod

            meta = MetaDataService.get_obj_by_slug(obj_slug, content_type)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(meta, context=context)
        return Response(serializer.data, status=HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if domain := self.request.query_params.get("city_domain"):
            context["city_domain"] = domain

        return context
