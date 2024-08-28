from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse
from api.permissions import ReadOnlyOrAdminPermission
from shop.models import Slider
from api.serializers import SliderSerializer

SLIDER_IMAGE_REQUEST_EXAMPLE = {
    "order": 1,
    "link": "https://example.com",
    "title": "test",
    "description": "test",
    "button_text": "test",
    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
    "tiny_image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
    "is_acitve": True,
}
SLIDER_IMAGE_RESPONSE_EXAMPLE = {"id": 1, **SLIDER_IMAGE_REQUEST_EXAMPLE}
SLIDER_IMAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(SLIDER_IMAGE_REQUEST_EXAMPLE.items())[:2]
}


@extend_schema_view(
    list=extend_schema(
        description="Получить список всех изображений слайдера на главной странице.",
        summary="Получить список всех изображений слайдера на главной странице",
        responses={200: SliderSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Sliders Example",
                summary="Example of listing all main page slider images",
                value=SLIDER_IMAGE_RESPONSE_EXAMPLE,
            )
        ],
    ),
    retrieve=extend_schema(
        description="Получить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Получение конкретного изображения слайдера главной страницы",
        responses={200: SliderSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Slider Example",
                summary="Пример извлечения конкретного изображения слайдера главной страницы",
                value=SLIDER_IMAGE_RESPONSE_EXAMPLE,
                response_only=True,
            )
        ],
    ),
    create=extend_schema(
        description="Создать новое изображение слайдера главной страницы.",
        summary="Создание нового изображения слайдера главной страницы",
        responses={201: SliderSerializer()},
        examples=[
            OpenApiExample(
                name="Create Slider Example",
                summary="Пример создания нового изображения слайдера главной страницы",
                value=SLIDER_IMAGE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Create Slider Response Example",
                summary="Пример ответа после создания нового изображения слайдера главной страницы",
                value=SLIDER_IMAGE_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Обновление конкретного изображения слайдера главной страницы",
        request=SliderSerializer,
        responses={200: SliderSerializer()},
        examples=[
            OpenApiExample(
                name="Update Slider Example",
                summary="Пример обновления конкретного изображения слайдера главной страницы",
                value=SLIDER_IMAGE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Update Slider Response Example",
                summary="Пример ответа после обновления конкретного изображения слайдера главной страницы",
                value=SLIDER_IMAGE_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Частичное обновление конкретного изображения слайдера главной страницы",
        request=SliderSerializer,
        responses={200: SliderSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Slider Example",
                summary="Пример частичного обновления конкретного изображения слайдера главной страницы",
                value=SLIDER_IMAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Partial Update Slider Response Example",
                summary="Пример ответа после частичного обновления конкретного изображения слайдера главной страницы",
                value=SLIDER_IMAGE_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Удаление конкретного изображения слайдера главной страницы",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Delete Slider Example",
                summary="Пример удаления конкретного изображения слайдера главной страницы",
                value=None,
            )
        ],
    ),
)
@extend_schema(tags=["Settings"])
class SliderViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, ModelViewSet):
    queryset = Slider.objects.all()
    serializer_class = SliderSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
