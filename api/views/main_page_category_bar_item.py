from rest_framework.viewsets import ModelViewSet


from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import MainPageCategoryBarItemSerializer
from shop.models import MainPageCategoryBarItem


CATEGORY_BAR_ITEM_REQUEST_EXAMPLE = {
    "order": 1,
    "link": "https://example.com/category1",
    "text": "Категория 1",
    "is_active": True,
}
CATEGORY_BAR_ITEM_RESPONSE_EXAMPLE = {
    "id": 1,
    **CATEGORY_BAR_ITEM_REQUEST_EXAMPLE,
}
CATEGORY_BAR_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(CATEGORY_BAR_ITEM_REQUEST_EXAMPLE.items())[:2]}


@extend_schema_view(
    list=extend_schema(
        description="Получить список всех элементов главного меню категорий",
        summary="Получить список всех элементов главного меню категорий",
        responses={200: MainPageCategoryBarItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Список элементов главного меню категорий",
                description="Пример успешного запроса",
                response_only=True,
                value=CATEGORY_BAR_ITEM_RESPONSE_EXAMPLE,
            )
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном элементе главного меню категорий по его идентификатору",
        summary="Получить информацию о конкретном элементе главного меню категорий",
        responses={200: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                name="Информация о элементе главного меню категорий",
                description="Пример успешного запроса",
                response_only=True,
                value=CATEGORY_BAR_ITEM_RESPONSE_EXAMPLE,
            )
        ],
    ),
    create=extend_schema(
        description="Создать новый элемент главного меню категорий",
        summary="Создать новый элемент главного меню категорий",
        request=MainPageCategoryBarItemSerializer,
        responses={201: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                name="Новый элемент главного меню категорий",
                description="Пример запроса на создание",
                request_only=True,
                value=CATEGORY_BAR_ITEM_REQUEST_EXAMPLE,
            ),
            OpenApiExample(
                name="Новый элемент главного меню категорий",
                description="Пример успешного ответа",
                response_only=True,
                value=CATEGORY_BAR_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о конкретном элементе главного меню категорий",
        summary="Обновить информацию о конкретном элементе главного меню категорий",
        request=MainPageCategoryBarItemSerializer,
        responses={200: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                name="Информация об обновленном элементе главного меню категорий",
                description="Пример запроса на обновление",
                request_only=True,
                value=CATEGORY_BAR_ITEM_REQUEST_EXAMPLE,
            ),
            OpenApiExample(
                name="Информация об обновленном элементе главного меню категорий",
                description="Пример ответа",
                response_only=True,
                value=CATEGORY_BAR_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о конкретном элементе главного меню категорий",
        summary="Частично обновить информацию о конкретном элементе главного меню категорий",
        request=MainPageCategoryBarItemSerializer,
        responses={200: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                request_only=True,
                name="Частичное обновление информации о конкретном элементе главного меню категорий",
                value=CATEGORY_BAR_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE,
            ),
            OpenApiExample(
                name="Частичное обновление информации о конкретном элементе главного меню категорий",
                description="Пример ответа",
                response_only=True,
                value=CATEGORY_BAR_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить конкретный элемент главного меню категорий",
        summary="Удалить конкретный элемент главного меню категорий",
        responses={204: None},
    ),
)
@extend_schema(tags=["Settings"])
class MainPageCategoryBarItemViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, ModelViewSet):

    queryset = MainPageCategoryBarItem.objects.all()
    serializer_class = MainPageCategoryBarItemSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
