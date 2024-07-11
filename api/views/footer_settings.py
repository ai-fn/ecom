from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.footer_settings import (
    FooterItemSerializer,
)
from shop.models import FooterItem
from rest_framework.viewsets import ModelViewSet


@extend_schema(
    tags=["Settings"],
)
class FooterItemViewSet(ModelViewSet):
    queryset = FooterItem.objects.all()
    serializer_class = FooterItemSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    pagination_class = None

    @extend_schema(
        summary="Получение списка всех элементов footer",
        description="Эта конечная точка получает список всех элементов footer.",
        responses={200: FooterItemSerializer()},
        examples=[
            OpenApiExample(
                "Пример списка всех элементов footer",
                summary="Пример списка всех элементов footer",
                response_only=True,
                description="Пример списка всех элементов footer",
                value=[
                    [
                        {
                            "id": 1,
                            "order": 1,
                            "title": "Элемент footer 1",
                            "link": "http://example.com",
                            "column": 1,
                            "is_acitve": True,
                        },
                        {
                            "id": 2,
                            "order": 2,
                            "title": "Элемент footer 2",
                            "link": "http://example.com",
                            "column": 1,
                            "is_acitve": True,
                        },
                        {
                            "id": 3,
                            "order": 3,
                            "title": "Элемент footer 3",
                            "link": "http://example.com",
                            "column": 1,
                            "is_acitve": True,
                        },
                    ],
                    [
                        {
                            "id": 1,
                            "order": 1,
                            "title": "Элемент footer 1",
                            "link": "http://example.com",
                            "column": 2,
                        },
                        {
                            "id": 2,
                            "order": 2,
                            "title": "Элемент footer 2",
                            "link": "http://example.com",
                            "column": 2,
                        },
                    ]
                ],
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().order_by("column", "order")
        grouped_footer_items = [
            self.serializer_class(queryset.filter(column=column), many=True).data
            for column in set(queryset.values_list("column", flat=True))
        ]

        return Response(grouped_footer_items)

    @extend_schema(
        summary="Получение конкретного элемента footer",
        description="Эта конечная точка получает конкретный элемент footer по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример получения конкретного элемента footer",
                response_only=True,
                summary="Пример получения конкретного элемента footer",
                description="Пример получения конкретного элемента footer",
                value={
                    "id": 1,
                    "order": 1,
                    "title": "Элемент footer 1",
                    "link": "http://example.com",
                    "column": 1,
                },
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Создание нового элемента footer",
        description="Эта конечная точка создает новый элемент footer.",
        examples=[
            OpenApiExample(
                "Пример создания нового элемента footer",
                summary="Пример создания нового элемента footer",
                description="Пример создания нового элемента footer",
                value={
                    "order": 1,
                    "title": "Элемент footer 1",
                    "link": "http://example.com",
                    "column": 1,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа на создание нового элемента footer",
                summary="Пример ответа на создание нового элемента footer",
                description="Пример ответа на создание нового элемента footer",
                value={
                    "id": 1,
                    "order": 1,
                    "title": "Элемент footer 1",
                    "link": "http://example.com",
                    "column": 1,
                },
                response_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление конкретного элемента footer",
        description="Эта конечная точка обновляет конкретный элемент footer по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример обновления конкретного элемента footer",
                summary="Пример обновления конкретного элемента footer",
                description="Пример обновления конкретного элемента footer",
                value={
                    "order": 1,
                    "title": "Обновленный элемент footer 1",
                    "link": "http://example.com",
                    "column": 1,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа на обновление конкретного элемента footer",
                summary="Пример ответа на обновление конкретного элемента footer",
                description="Пример ответа на обновление конкретного элемента footer",
                value={
                    "id": 1,
                    "order": 1,
                    "title": "Обновленный элемент footer 1",
                    "link": "http://example.com",
                    "column": 1,
                },
                response_only=True,
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление конкретного элемента footer",
        description="Эта конечная точка выполняет частичное обновление конкретного элемента footer по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример частичного обновления конкретного элемента footer",
                request_only=True,
                summary="Пример частичного обновления конкретного элемента footer",
                description="Пример частичного обновления конкретного элемента footer",
                value={"title": "Обновленный элемент footer 2"},
            ),
            OpenApiExample(
                "Пример частичного обновления конкретного элемента footer",
                response_only=True,
                summary="Пример частичного обновления конкретного элемента footer",
                description="Пример частичного обновления конкретного элемента footer",
                value={
                    "id": 1,
                    "order": 1,
                    "title": "Обновленный элемент footer 2",
                    "link": "http://example.com",
                    "column": 1,
                },
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление конкретного элемента footer",
        description="Эта конечная точка удаляет конкретный элемент footer по его идентификатору.",
        examples=[
            OpenApiExample(
                name="Пример удаления конкретного элемента footer",
                summary="Пример удаления конкретного элемента footer",
                description="Пример удаления конкретного элемента footer",
                value=None,
                request_only=True,
            )
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
