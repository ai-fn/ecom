from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse
from api.permissions import ReadOnlyOrAdminPermission
from shop.models import Banner
from api.serializers import BannerSerializer

BANNER_IMAGE_REQUEST_EXAMPLE = {
    "order": 1,
    "link": "https://example.com",
    "title": "test",
    "description": "test",
    "button_text": "test",
    "image": "https://s3.aws.cloud/main/banners/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
    "tiny_image": "https://s3.aws.cloud/main/banners/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
    "is_acitve": True,
}
BANNER_IMAGE_RESPONSE_EXAMPLE = {"id": 1, **BANNER_IMAGE_REQUEST_EXAMPLE}
BANNER_IMAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(BANNER_IMAGE_REQUEST_EXAMPLE.items())[:2]
}


@extend_schema_view(
    list=extend_schema(
        description="Получить список всех банеров.",
        summary="Получить список всех банеров.",
        responses={200: BannerSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Banners Example",
                summary="Example of listing all main page BANNER images",
                value=BANNER_IMAGE_RESPONSE_EXAMPLE,
            )
        ],
    ),
    retrieve=extend_schema(
        description="Получить конкретный банер по его идентификатору.",
        summary="Получение конкретного банера.",
        responses={200: BannerSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Banner Example",
                summary="Пример извлечения конкретного банера.",
                value=BANNER_IMAGE_RESPONSE_EXAMPLE,
                response_only=True,
            )
        ],
    ),
    create=extend_schema(
        description="Создать новое банер.",
        summary="Создание нового банера.",
        responses={201: BannerSerializer()},
        examples=[
            OpenApiExample(
                name="Create Banner Example",
                summary="Пример создания нового банера.",
                value=BANNER_IMAGE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Create Banner Response Example",
                summary="Пример ответа после создания нового банера.",
                value=BANNER_IMAGE_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить конкретный банер по его идентификатору.",
        summary="Обновление конкретного банера.",
        request=BannerSerializer,
        responses={200: BannerSerializer()},
        examples=[
            OpenApiExample(
                name="Update Banner Example",
                summary="Пример обновления конкретного банера.",
                value=BANNER_IMAGE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Update Banner Response Example",
                summary="Пример ответа после обновления конкретного банера.",
                value=BANNER_IMAGE_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить конкретный банер по его идентификатору.",
        summary="Частичное обновление конкретного банера.",
        request=BannerSerializer,
        responses={200: BannerSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Banner Example",
                summary="Пример частичного обновления конкретного банера.",
                value=BANNER_IMAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Partial Update Banner Response Example",
                summary="Пример ответа после частичного обновления конкретного банера.",
                value=BANNER_IMAGE_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить конкретный банер по его идентификатору.",
        summary="Удаление конкретного банера.",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Delete Banner Example",
                summary="Пример удаления конкретного банера.",
                value=None,
            )
        ],
    ),
)
@extend_schema(tags=["Settings"])
class BannerViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
