from rest_framework.viewsets import ModelViewSet


from drf_spectacular.utils import extend_schema, OpenApiExample

from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import MainPageCategoryBarItemSerializer
from shop.models import MainPageCategoryBarItem


@extend_schema(tags=["Settings"])
class MainPageCategoryBarItemViewSet(ModelViewSet):

    queryset = MainPageCategoryBarItem.objects.all()
    serializer_class = MainPageCategoryBarItemSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех элементов главного меню категорий",
        summary="Получить список всех элементов главного меню категорий",
        responses={200: MainPageCategoryBarItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Список элементов главного меню категорий",
                description="Пример успешного запроса",
                response_only=True,
                value={
                    "order": 1,
                    "link": "https://example.com/category1",
                    "text": "Категория 1",
                },
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        """
        Получить список всех элементов главного меню категорий.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном элементе главного меню категорий по его идентификатору",
        summary="Получить информацию о конкретном элементе главного меню категорий",
        responses={200: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                name="Информация о элементе главного меню категорий",
                description="Пример успешного запроса",
                response_only=True,
                value={
                    "id": 1,
                    "order": 1,
                    "link": "https://example.com/category1",
                    "text": "Категория 1",
                },
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получить информацию о конкретном элементе главного меню категорий.
        """
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создать новый элемент главного меню категорий",
        summary="Создать новый элемент главного меню категорий",
        request=MainPageCategoryBarItemSerializer,
        responses={201: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                name="Новый элемент главного меню категорий",
                description="Пример запроса на создание",
                request_only=True,
                value={
                    "order": 3,
                    "link": "https://example.com/category3",
                    "text": "Категория 3",
                },
            ),
            OpenApiExample(
                name="Новый элемент главного меню категорий",
                description="Пример успешного ответа",
                response_only=True,
                value={
                    "id": 3,
                    "order": 3,
                    "link": "https://example.com/category3",
                    "text": "Категория 3",
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        """
        Создать новый элемент главного меню категорий.
        """
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о конкретном элементе главного меню категорий",
        summary="Частично обновить информацию о конкретном элементе главного меню категорий",
        request=MainPageCategoryBarItemSerializer,
        responses={200: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                request_only=True,
                name="Частичное обновление информации о конкретном элементе главного меню категорий",
                value={"text": "Категоря 2"},
            ),
            OpenApiExample(
                name="Частичное обновление информации о конкретном элементе главного меню категорий",
                description="Пример ответа",
                response_only=True,
                value={
                    "id": 3,
                    "order": 3,
                    "text": "Категория 2",
                    "link": "https://example.com/category1-updated",
                },
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Частично обновить информацию о конкретном элементе главного меню категорий.
        """
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о конкретном элементе главного меню категорий",
        summary="Обновить информацию о конкретном элементе главного меню категорий",
        request=MainPageCategoryBarItemSerializer,
        responses={200: MainPageCategoryBarItemSerializer()},
        examples=[
            OpenApiExample(
                name="Информация об обновленном элементе главного меню категорий",
                description="Пример запроса на обновление",
                request_only=True,
                value={
                    "order": 1,
                    "link": "https://example.com/category1-updated",
                    "text": "Категория 1 (обновлено)",
                },
            ),
            OpenApiExample(
                name="Информация об обновленном элементе главного меню категорий",
                description="Пример ответа",
                response_only=True,
                value={
                    "id": 1,
                    "order": 1,
                    "link": "https://example.com/category1-updated",
                    "text": "Категория 1 (обновлено)",
                },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        """
        Обновить информацию о конкретном элементе главного меню категорий.
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить конкретный элемент главного меню категорий",
        summary="Удалить конкретный элемент главного меню категорий",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        """
        Удалить конкретный элемент главного меню категорий.
        """
        return super().destroy(request, *args, **kwargs)
