from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiExample

from api.permissions import ReadOnlyOrAdminPermission
from shop.models import MainPageSliderImage
from api.serializers import MainPageSliderImageSerializer


@extend_schema(tags=["Settings"])
class MainPageSliderImageViewSet(ModelViewSet):
    queryset = MainPageSliderImage.objects.all()
    serializer_class = MainPageSliderImageSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех изображений слайдера на главной странице.",
        summary="Получить список всех изображений слайдера на главной странице",
        responses={200: MainPageSliderImageSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List MainPageSliderImages Example",
                summary="Example of listing all main page slider images",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "https://alta-profil.net",
                    "title": "test",
                    "description": "test",
                    "button_text": "test",
                    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
                    "thumb_img": "base64string",
                },
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Получение конкретного изображения слайдера главной страницы",
        responses={200: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve MainPageSliderImage Example",
                summary="Пример извлечения конкретного изображения слайдера главной страницы",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "https://alta-profil.net",
                    "title": "test",
                    "description": "test",
                    "button_text": "test",
                    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
                    "thumb_img": "base64string",
                },
                response_only=True,
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создать новое изображение слайдера главной страницы.",
        summary="Создание нового изображения слайдера главной страницы",
        responses={201: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Create MainPageSliderImage Example",
                summary="Пример создания нового изображения слайдера главной страницы",
                value={
                    "order": 1,
                    "link": "https://alta-profil.net",
                    "title": "test",
                    "description": "test",
                    "button_text": "test",
                    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
                    "thumb_img": "base64string",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Create MainPageSliderImage Response Example",
                summary="Пример ответа после создания нового изображения слайдера главной страницы",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "https://alta-profil.net",
                    "title": "test",
                    "description": "test",
                    "button_text": "test",
                    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
                    "thumb_img": "base64string",
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Обновление конкретного изображения слайдера главной страницы",
        request=MainPageSliderImageSerializer,
        responses={200: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Update MainPageSliderImage Example",
                summary="Пример обновления конкретного изображения слайдера главной страницы",
                value={
                    "order": 1,
                    "link": "https://alta-profil.net",
                    "title": "test",
                    "description": "test",
                    "button_text": "test",
                    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
                    "thumb_img": "base64string",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Update MainPageSliderImage Response Example",
                summary="Пример ответа после обновления конкретного изображения слайдера главной страницы",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "https://alta-profil.net",
                    "title": "test",
                    "description": "test",
                    "button_text": "test",
                    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
                    "thumb_img": "base64string",
                },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Частичное обновление конкретного изображения слайдера главной страницы",
        request=MainPageSliderImageSerializer,
        responses={200: MainPageSliderImageSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update MainPageSliderImage Example",
                summary="Пример частичного обновления конкретного изображения слайдера главной страницы",
                value={"title": "Updated Title 1"},
                request_only=True,
            ),
            OpenApiExample(
                name="Partial Update MainPageSliderImage Response Example",
                summary="Пример ответа после частичного обновления конкретного изображения слайдера главной страницы",
                value={
                    "id": 1,
                    "order": 1,
                    "link": "https://alta-profil.net",
                    "title": "test",
                    "description": "test",
                    "button_text": "test",
                    "image": "/media/main/sliders/image-c25b479e-06d4-46a5-a26a-f2094e914383.webp",
                    "thumb_img": "base64string",
                },
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить конкретное изображение слайдера главной страницы по его идентификатору.",
        summary="Удаление конкретного изображения слайдера главной страницы",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Delete MainPageSliderImage Example",
                summary="Пример удаления конкретного изображения слайдера главной страницы",
                value=None,
            )
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
