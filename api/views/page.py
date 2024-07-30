from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from api.serializers import PageSerializer
from shop.models import Page


@extend_schema(
    tags=["Shop"]
)
@extend_schema_view(
    list=extend_schema(
        summary="Получить список страниц",
        description="Возвращает список всех страниц.",
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value=[
                            {
                                "id": 1,
                                "title": "Первая страница",
                                "description": "Описание первой страницы",
                                "slug": "pervaya-stranitsa",
                                "image": "/media/pages/image1.jpg",
                                "opengraph_metadata": {
                                    "title": "OG Title",
                                    "description": "OG Description",
                                    "OpenGraph": {
                                        "url": "http://example.com",
                                        "siteName": "Example Site",
                                        "images": [
                                            {
                                                "id": 1,
                                                "image": "/media/pages/og_image.jpg",
                                                "width": 800,
                                                "height": 600
                                            }
                                        ],
                                        "locale": "en_US",
                                        "type": "website"
                                    }
                                }
                            }
                        ]
                    )
                ]
            )
        }
    ),
    retrieve=extend_schema(
        summary="Получить страницу",
        description="Возвращает детальную информацию о конкретной странице.",
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value={
                            "id": 1,
                            "title": "Первая страница",
                            "description": "Описание первой страницы",
                            "slug": "pervaya-stranitsa",
                            "image": "/media/pages/image1.jpg",
                            "opengraph_metadata": {
                                "title": "OG Title",
                                "description": "OG Description",
                                "OpenGraph": {
                                    "url": "http://example.com",
                                    "siteName": "Example Site",
                                    "images": [
                                        {
                                            "id": 1,
                                            "image": "/media/pages/og_image.jpg",
                                            "width": 800,
                                            "height": 600
                                        }
                                    ],
                                    "locale": "en_US",
                                    "type": "website"
                                }
                            }
                        }
                    )
                ]
            )
        }
    ),
    create=extend_schema(
        summary="Создать страницу",
        description="Создает новую страницу.",
        request=PageSerializer,
        responses={
            201: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value={
                            "id": 2,
                            "title": "Новая страница",
                            "description": "Описание новой страницы",
                            "slug": "novaya-stranitsa",
                            "image": None,
                            "opengraph_metadata": {
                                "title": "OG Title",
                                "description": "OG Description",
                                "OpenGraph": {
                                    "url": "http://example.com",
                                    "siteName": "Example Site",
                                    "images": [
                                        {
                                            "id": 1,
                                            "image": "/media/pages/og_image.jpg",
                                            "width": 800,
                                            "height": 600
                                        }
                                    ],
                                    "locale": "en_US",
                                    "type": "website"
                                }
                            }
                        }
                    )
                ]
            )
        }
    ),
    update=extend_schema(
        summary="Обновить страницу",
        description="Обновляет существующую страницу.",
        request=PageSerializer,
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value={
                            "id": 1,
                            "title": "Обновленная страница",
                            "description": "Обновленное описание страницы",
                            "slug": "obnovlennaya-stranitsa",
                            "image": None,
                            "opengraph_metadata": {
                                "title": "OG Title",
                                "description": "OG Description",
                                "OpenGraph": {
                                    "url": "http://example.com",
                                    "siteName": "Example Site",
                                    "images": [
                                        {
                                            "id": 1,
                                            "image": "/media/pages/og_image.jpg",
                                            "width": 800,
                                            "height": 600
                                        }
                                    ],
                                    "locale": "en_US",
                                    "type": "website"
                                }
                            }
                        }
                    )
                ]
            )
        }
    ),
    partial_update=extend_schema(
        summary="Частично обновить страницу",
        description="Частично обновляет существующую страницу.",
        request=PageSerializer,
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value={
                            "id": 1,
                            "title": "Частично обновленная страница",
                            "description": "Описание первой страницы",
                            "slug": "pervaya-stranitsa",
                            "image": "/media/pages/image1.jpg",
                            "opengraph_metadata": {
                                "title": "OG Title",
                                "description": "OG Description",
                                "OpenGraph": {
                                    "url": "http://example.com",
                                    "siteName": "Example Site",
                                    "images": [
                                        {
                                            "id": 1,
                                            "image": "/media/pages/og_image.jpg",
                                            "width": 800,
                                            "height": 600
                                        }
                                    ],
                                    "locale": "en_US",
                                    "type": "website"
                                }
                            }
                        }
                    )
                ]
            )
        }
    ),
    destroy=extend_schema(
        summary="Удалить страницу",
        description="Удаляет существующую страницу.",
        responses={
            204: OpenApiResponse(
                response=None,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value=None
                    )
                ]
            )
        }
    )
)
class PageViewSet(ModelViewSet):
    queryset = Page.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = PageSerializer
