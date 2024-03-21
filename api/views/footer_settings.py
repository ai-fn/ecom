from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, OpenApiExample

from api.serializers.footer_settings import FooterItemSerializer, FooterSettingSerializer
from shop.models import FooterItem, FooterSettings


@extend_schema(
    tags=["Settings"]
)
class FooterSettingsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = FooterSettingSerializer
    queryset = FooterSettings.objects.all()

    @extend_schema(
        summary="Получение списка всех настроек нижнего колонтитула",
        description="Эта конечная точка получает список всех настроек нижнего колонтитула.",
        examples=[
            OpenApiExample(
                "Пример настроек нижнего колонтитула списка",
                summary="Пример списка всех настроек нижнего колонтитула",
                description="Пример списка всех настроек нижнего колонтитула",
                value=[
                    {"max_footer_items": 5},
                    {"max_footer_items": 10},
                    {"max_footer_items": 15}
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Получение конкретной настройки нижнего колонтитула",
        description="Эта конечная точка получает конкретную настройку нижнего колонтитула по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример получения конкретной настройки нижнего колонтитула",
                summary="Пример получения конкретной настройки нижнего колонтитула",
                description="Пример получения конкретной настройки нижнего колонтитула",
                value={"max_footer_items": 5}
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Создание новой настройки нижнего колонтитула",
        description="Эта конечная точка создаёт новую настройку нижнего колонтитула.",
        examples=[
            OpenApiExample(
                "Пример создания новой настройки нижнего колонтитула",
                summary="Пример создания новой настройки нижнего колонтитула",
                description="Пример создания новой настройки нижнего колонтитула",
                value={"max_footer_items": 5}
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление конкретной настройки нижнего колонтитула",
        description="Эта конечная точка обновляет конкретную настройку нижнего колонтитула по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример обновления конкретной настройки нижнего колонтитула",
                summary="Пример обновления конкретной настройки нижнего колонтитула",
                description="Пример обновления конкретной настройки нижнего колонтитула",
                value={"max_footer_items": 5}
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление конкретной настройки нижнего колонтитула",
        description="Эта конечная точка выполняет частичное обновление конкретной настройки нижнего колонтитула по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример частичного обновления конкретной настройки нижнего колонтитула",
                summary="Пример частичного обновления конкретной настройки нижнего колонтитула",
                description="Пример частичного обновления конкретной настройки нижнего колонтитула",
                value={"max_footer_items": 5}
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление конкретной настройки нижнего колонтитула",
        description="Эта конечная точка удаляет конкретную настройку нижнего колонтитула по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример удаления конкретной настройки нижнего колонтитула",
                summary="Пример удаления конкретной настройки нижнего колонтитула",
                description="Пример удаления конкретной настройки нижнего колонтитула",
                value=None
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)



@extend_schema(
    tags=["Settings"],
)
class FooterItemViewSet(viewsets.ModelViewSet):
    queryset = FooterItem.objects.all()
    serializer_class = FooterItemSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Получение списка всех элементов нижнего колонтитула",
        description="Эта конечная точка получает список всех элементов нижнего колонтитула.",
        examples=[
            OpenApiExample(
                "Пример списка всех элементов нижнего колонтитула",
                summary="Пример списка всех элементов нижнего колонтитула",
                description="Пример списка всех элементов нижнего колонтитула",
                value=[
                    {"order": 1, "title": "Элемент нижнего колонтитула 1", "link": "http://example.com"},
                    {"order": 2, "title": "Элемент нижнего колонтитула 2", "link": "http://example.com"},
                    {"order": 3, "title": "Элемент нижнего колонтитула 3", "link": "http://example.com"}
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Получение конкретного элемента нижнего колонтитула",
        description="Эта конечная точка получает конкретный элемент нижнего колонтитула по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример получения конкретного элемента нижнего колонтитула",
                summary="Пример получения конкретного элемента нижнего колонтитула",
                description="Пример получения конкретного элемента нижнего колонтитула",
                value={"order": 1, "title": "Элемент нижнего колонтитула 1", "link": "http://example.com"}
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Создание нового элемента нижнего колонтитула",
        description="Эта конечная точка создает новый элемент нижнего колонтитула.",
        examples=[
            OpenApiExample(
                "Пример создания нового элемента нижнего колонтитула",
                summary="Пример создания нового элемента нижнего колонтитула",
                description="Пример создания нового элемента нижнего колонтитула",
                value={"order": 1, "title": "Элемент нижнего колонтитула 1", "link": "http://example.com"}
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление конкретного элемента нижнего колонтитула",
        description="Эта конечная точка обновляет конкретный элемент нижнего колонтитула по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример обновления конкретного элемента нижнего колонтитула",
                summary="Пример обновления конкретного элемента нижнего колонтитула",
                description="Пример обновления конкретного элемента нижнего колонтитула",
                value={"order": 1, "title": "Обновленный элемент нижнего колонтитула 1", "link": "http://example.com"}
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление конкретного элемента нижнего колонтитула",
        description="Эта конечная точка выполняет частичное обновление конкретного элемента нижнего колонтитула по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример частичного обновления конкретного элемента нижнего колонтитула",
                summary="Пример частичного обновления конкретного элемента нижнего колонтитула",
                description="Пример частичного обновления конкретного элемента нижнего колонтитула",
                value={"title": "Обновленный элемент нижнего колонтитула 1"}
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Удаление конкретного элемента нижнего колонтитула",
        description="Эта конечная точка удаляет конкретный элемент нижнего колонтитула по его идентификатору.",
        examples=[
            OpenApiExample(
                name="Пример удаления конкретного элемента нижнего колонтитула",
                summary="Пример удаления конкретного элемента нижнего колонтитула",
                description="Пример удаления конкретного элемента нижнего колонтитула",
                value=None
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
