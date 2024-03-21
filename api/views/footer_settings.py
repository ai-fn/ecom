from drf_spectacular.utils import extend_schema, OpenApiExample

from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.footer_settings import FooterItemSerializer, FooterSettingSerializer
from shop.models import FooterItem, FooterSettings


@extend_schema(
    tags=["Settings"]
)
class FooterSettingsViewSet(viewsets.ModelViewSet):
    permission_classes = [ReadOnlyOrAdminPermission]
    serializer_class = FooterSettingSerializer
    queryset = FooterSettings.objects.all()

    @extend_schema(
        summary="Получение списка всех настроек footer",
        description="Эта конечная точка получает список всех настроек footer.",
        examples=[
            OpenApiExample(
                "Пример настроек footer списка",
                summary="Пример списка всех настроек footer",
                response_only=True,
                description="Пример списка всех настроек footer",
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
        summary="Получение конкретной настройки footer",
        description="Эта конечная точка получает конкретную настройку footer по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример получения конкретной настройки footer",
                response_only=True,
                summary="Пример получения конкретной настройки footer",
                description="Пример получения конкретной настройки footer",
                value={"max_footer_items": 5}
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Создание новой настройки footer",
        description="Эта конечная точка создаёт новую настройку footer.",
        examples=[
            OpenApiExample(
                "Пример создания новой настройки footer",
                summary="Пример создания новой настройки footer",
                description="Пример создания новой настройки footer",
                value={"max_footer_items": 5}
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление конкретной настройки footer",
        description="Эта конечная точка обновляет конкретную настройку footer по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример обновления конкретной настройки footer",
                summary="Пример обновления конкретной настройки footer",
                description="Пример обновления конкретной настройки footer",
                value={"max_footer_items": 5}
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление конкретной настройки footer",
        description="Эта конечная точка выполняет частичное обновление конкретной настройки footer по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример частичного обновления конкретной настройки footer",
                summary="Пример частичного обновления конкретной настройки footer",
                description="Пример частичного обновления конкретной настройки footer",
                value={"max_footer_items": 2}
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление конкретной настройки footer",
        description="Эта конечная точка удаляет конкретную настройку footer по её идентификатору.",
        examples=[
            OpenApiExample(
                "Пример удаления конкретной настройки footer",
                summary="Пример удаления конкретной настройки footer",
                description="Пример удаления конкретной настройки footer",
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
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        summary="Получение списка всех элементов footer",
        description="Эта конечная точка получает список всех элементов footer.",
        examples=[
            OpenApiExample(
                "Пример списка всех элементов footer",
                summary="Пример списка всех элементов footer",
                response_only=True,
                description="Пример списка всех элементов footer",
                value=[
                    {"order": 1, "title": "Элемент footer 1", "link": "http://example.com"},
                    {"order": 2, "title": "Элемент footer 2", "link": "http://example.com"},
                    {"order": 3, "title": "Элемент footer 3", "link": "http://example.com"}
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Получение конкретного элемента footer",
        description="Эта конечная точка получает конкретный элемент footer по его идентификатору.",
        examples=[
            OpenApiExample(
                "Пример получения конкретного элемента footer",
                response_only=True,
                summary="Пример получения конкретного элемента footer",
                description="Пример получения конкретного элемента footer",
                value={"order": 1, "title": "Элемент footer 1", "link": "http://example.com"}
            )
        ]
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
                value={"order": 1, "title": "Элемент footer 1", "link": "http://example.com"}
            )
        ]
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
                value={"order": 1, "title": "Обновленный элемент footer 1", "link": "http://example.com"}
            )
        ]
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
                value={"title": "Обновленный элемент footer 2"}
            ),
            OpenApiExample(
                "Пример частичного обновления конкретного элемента footer",
                response_only=True,
                summary="Пример частичного обновления конкретного элемента footer",
                description="Пример частичного обновления конкретного элемента footer",
                value={"order": 1, "title": "Обновленный элемент footer 2", "link": "http://example.com"}
            )
        ]
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
                value=None
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
