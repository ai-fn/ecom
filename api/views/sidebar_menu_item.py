from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.serializers import SideBarMenuItemSerializer
from shop.models import SideBarMenuItem
from api.permissions import ReadOnlyOrAdminPermission


SIDE_BAR_MENU_ITEM_REQEUST_EXAMPLE = {
                    "order": 1,
                    "title": "Dummy title",
                    "icon": "delivery",
                    "link": "/katalog/",
                }
SIDE_BAR_MENU_ITEM_RESPONSE_EXAMPLE = {
                    "id": 1,
**SIDE_BAR_MENU_ITEM_REQEUST_EXAMPLE,
}
SIDE_BAR_MENU_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(SIDE_BAR_MENU_ITEM_REQEUST_EXAMPLE.items())[:2]}


@extend_schema_view(
    list=extend_schema(
        description="Получение списка элементов бокового меню",
        summary="Получение списка элементов бокового меню",
        examples=[
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value=SIDE_BAR_MENU_ITEM_RESPONSE_EXAMPLE,
            )
        ],
    ),
    retrieve=extend_schema(
        description="Получение элемента бокового меню по уникальному идентификатору",
        summary="Получение элемента бокового меню по уникальному идентификатору",
        examples=[
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value=SIDE_BAR_MENU_ITEM_RESPONSE_EXAMPLE,
            )
        ],
    ),
    create=extend_schema(
        description="Создание элемента бокового меню",
        summary="Создание элемента бокового меню",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                description="Пример запроса",
                request_only=True,
                value=SIDE_BAR_MENU_ITEM_REQEUST_EXAMPLE,
            ),
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value=SIDE_BAR_MENU_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    update=extend_schema(
        description="Обновление элемента бокового меню",
        summary="Обновление элемента бокового меню",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                description="Пример запроса",
                request_only=True,
                value=SIDE_BAR_MENU_ITEM_REQEUST_EXAMPLE,
            ),
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value=SIDE_BAR_MENU_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частичное обновление элемента бокового меню",
        summary="Частичное обновление элемента бокового меню",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                description="Пример запроса",
                request_only=True,
                value=SIDE_BAR_MENU_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE,
            ),
            OpenApiExample(
                name="Пример ответа",
                description="Пример ответа",
                response_only=True,
                value=SIDE_BAR_MENU_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удаление элемента бокового меню",
        summary="Удаление элемента бокового меню",
    ),
)
@extend_schema(tags=["Shop"])
class SideBarMenuItemViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):

    queryset = SideBarMenuItem.objects.order_by("-created_at")
    serializer_class = SideBarMenuItemSerializer
    permission_classes = (ReadOnlyOrAdminPermission,)
