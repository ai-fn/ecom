from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from api.serializers import PageSerializer
from shop.models import Page
from api.views.metadata import OPEN_GRAPH_META_RESPONSE_EXAMPLE


PAGE_REQUEST_EXAMPLE = {
    "title": "Первая страница",
    "h1_tag": "dummy_h1_tag",
    "description": "Описание первой страницы",
    "slug": "pervaya-stranitsa",
    "image": "/media/pages/image1.jpg",
}
PAGE_RESPONSE_EXAMPLE = {
    "id": 1,
    **PAGE_REQUEST_EXAMPLE,
    "opengraph_metadata": OPEN_GRAPH_META_RESPONSE_EXAMPLE,
}
PAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(PAGE_REQUEST_EXAMPLE.items())[:2]}


@extend_schema(tags=["Shop"])
@extend_schema_view(
    list=extend_schema(
        summary="Получить список страниц",
        description="Возвращает список всех страниц.",
        responses={
            200: OpenApiResponse(
                response=PageSerializer(many=True),
                examples=[OpenApiExample("Пример успешного ответа", value=[])],
            )
        },
    ),
    retrieve=extend_schema(
        summary="Получить страницу",
        description="Возвращает детальную информацию о конкретной странице.",
        responses={
            200: OpenApiResponse(
                response=PageSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
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
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PAGE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
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
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PAGE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]

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
                        "Пример успешного ответа",
                        value=PAGE_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PAGE_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    destroy=extend_schema(
        summary="Удалить страницу",
        description="Удаляет существующую страницу.",
        responses={
            204: OpenApiResponse(
                response=None,
                examples=[OpenApiExample("Пример успешного ответа", value=None)],
            )
        },
    ),
)
class PageViewSet(ModelViewSet):
    queryset = Page.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = PageSerializer

    def get_object(self) -> Page:
        loogup_field: str = self.kwargs.get(self.lookup_field)

        if loogup_field and not loogup_field.isdigit():
            self.lookup_field = self.lookup_url_kwarg = "slug"
            self.kwargs[self.lookup_field] = loogup_field

        return super().get_object()
