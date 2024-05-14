from loguru import logger
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.decorators import action

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from PIL import Image
from drf_spectacular.utils import extend_schema, OpenApiParameter


from api.serializers import OpenGraphMetaSerializer
from shop.models import ImageMetaData, OpenGraphMeta


@extend_schema(tags=["Shop"])
class MetadataViewSet(GenericViewSet):
    queryset = OpenGraphMeta.objects.all()
    permission_classes = [AllowAny]
    serializer_class = OpenGraphMetaSerializer

    @extend_schema(
        description="Получение метаданных",
        summary="Получение метаданных",
        parameters=[
            OpenApiParameter(
                name="content_type",
                description="Наименование страницы",
                default="Главная страница",
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
    def get_metadata(self, request, *args, **kwargs):
        content_type = request.query_params.get("content_type")
        city_domain = request.query_params.get("city_domain")
        obj_slug = request.query_params.get("slug")
        try:
            tp = ContentType.objects.get(model=content_type)
            model = tp.model_class()
        except ContentType.DoesNotExist:
            return Response({"error": _("unknown content type")}, status=HTTP_400_BAD_REQUEST)

        try:
            instance = model.objects.get(slug=obj_slug)
        except model.DoesNotExist:
            return Response({"error": _(f"{model.__name__} with provided slug not found")}, status=HTTP_400_BAD_REQUEST)
            
        meta = self._get_obj_metadata(instance, request, tp)

        serializer = self.get_serializer(meta)
        return Response(serializer.data, status=HTTP_200_OK)

    def _get_obj_metadata(self, obj, request, content_type):
        title = getattr(obj, "title", "") or getattr(obj, "name", "")
        description = getattr(obj, "description", "Нет описания")
        image = getattr(obj, "image", None)
        images = getattr(obj, "images", None)
        domain = request.query_params.get("city_domain")

        meta, _ = OpenGraphMeta.objects.get_or_create(
            object_id=obj.id,
            content_type=content_type,
            defaults={
                "title": title,
                "description": description,
                "site_name": "Кров маркет",
                "locale": "ru_RU",
                "url": f"{request.scheme}://{domain}/{obj.get_absolute_url()}" if hasattr(obj, "get_absolute_url") else f"/{self.slug}/"
            }
        )

        if images:
            for img in images.all():
                self._get_image_meta_data(meta, img)
        elif image:
            self._get_image_meta_data(meta, image)

        return meta
    
    def _get_image_meta_data(self, meta, image):
        img_url = getattr(image, "url", None) or getattr(image.image, "url", None)
        img_file = getattr(image, "file", None) or getattr(image.image, "file", None)
        width, height = 0, 0

        if not img_url or not img_file:
            return

        try:
            with Image.open(img_file.name) as img:
                width, height = img.size
        except OSError:
            logger.error("error while open metadata image")
            return

        img_url = "/".join(img_url.split("/")[2:])

        ImageMetaData.objects.get_or_create(
            open_graph_meta=meta,
            image=img_url,
            defaults={
                "width": width,
                "height": height,
                "image": img_url
            },
        )
