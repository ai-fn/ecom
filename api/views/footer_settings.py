from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.footer_settings import (
    FooterItemSerializer,
)
from shop.models import FooterItem
from rest_framework.viewsets import ModelViewSet


FOOTER_ITEM_REQUEST_EXAMPLE = {
    "order": 1,
    "title": "Элемент footer 1",
    "link": "http://example.com",
    "column": 1,
    "is_acitve": True,
}
FOOTER_ITEM_RESPONSE_EXAMPLE = {
    "id": 1,
    **FOOTER_ITEM_REQUEST_EXAMPLE,
}
FOOTER_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(FOOTER_ITEM_REQUEST_EXAMPLE.items())[:2]}


@extend_schema_view(
    list=extend_schema(
        summary="Получение списка всех элементов footer",
        description="Эта конечная точка получает список всех элементов footer.",
        responses={200: FooterItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Пример списка всех элементов footer",
                summary="Пример списка всех элементов footer",
                response_only=True,
                description="Пример списка всех элементов footer",
                value=FOOTER_ITEM_RESPONSE_EXAMPLE,
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Получение конкретного элемента footer",
        description="Эта конечная точка получает конкретный элемент footer по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример получения конкретного элемента footer",
                response_only=True,
                summary="Пример получения конкретного элемента footer",
                description="Пример получения конкретного элемента footer",
                value=FOOTER_ITEM_RESPONSE_EXAMPLE,
            )
        ],
    ),
    create=extend_schema(
        summary="Создание нового элемента footer",
        description="Эта конечная точка создает новый элемент footer.",
        examples=[
            OpenApiExample(
                "Пример создания нового элемента footer",
                summary="Пример создания нового элемента footer",
                description="Пример создания нового элемента footer",
                value=FOOTER_ITEM_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа на создание нового элемента footer",
                summary="Пример ответа на создание нового элемента footer",
                description="Пример ответа на создание нового элемента footer",
                value=FOOTER_ITEM_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Обновление конкретного элемента footer",
        description="Эта конечная точка обновляет конкретный элемент footer по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример обновления конкретного элемента footer",
                summary="Пример обновления конкретного элемента footer",
                description="Пример обновления конкретного элемента footer",
                value=FOOTER_ITEM_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа на обновление конкретного элемента footer",
                summary="Пример ответа на обновление конкретного элемента footer",
                description="Пример ответа на обновление конкретного элемента footer",
                value=FOOTER_ITEM_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частичное обновление конкретного элемента footer",
        description="Эта конечная точка выполняет частичное обновление конкретного элемента footer по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример частичного обновления конкретного элемента footer",
                request_only=True,
                summary="Пример частичного обновления конкретного элемента footer",
                description="Пример частичного обновления конкретного элемента footer",
                value=FOOTER_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE,
            ),
            OpenApiExample(
                "Пример частичного обновления конкретного элемента footer",
                response_only=True,
                summary="Пример частичного обновления конкретного элемента footer",
                description="Пример частичного обновления конкретного элемента footer",
                value=FOOTER_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    destroy=extend_schema(
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
    ),
)
@extend_schema(
    tags=["Settings"],
)
class FooterItemViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, ModelViewSet):
    queryset = FooterItem.objects.all()
    serializer_class = FooterItemSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    pagination_class = None


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        grouped_footer_items = [
            self.serializer_class(queryset.filter(column=column), many=True).data
            for column in set(queryset.values_list("column", flat=True))
        ]

        return Response(grouped_footer_items)
