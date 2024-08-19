from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.brand import BrandSerializer
from shop.models import Brand
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample


REQUEST_EXAMPLE = {
    "name": "Deke",
    "h1_tag": "dummy_h1_tag",
    "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
    "order": 1,
    "is_acitve": True,
}

BRAND_RESPONSE_EXAMPLE = {
    "id": 1,
    **REQUEST_EXAMPLE,
}
PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(REQUEST_EXAMPLE.items())[:2]}

@extend_schema_view(
    list=extend_schema(
        description="Получить список всех брендов",
        summary="Список брендов",
        responses={200: BrandSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="response",
                value=BRAND_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном бренде",
        summary="Информация о бренде",
        responses={200: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="response",
                value=BRAND_RESPONSE_EXAMPLE,
            )
        ],
    ),
    create=extend_schema(
        description="Создать новый бренд",
        summary="Создание бренда",
        responses={201: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="request",
                value=REQUEST_EXAMPLE,
            ),
            OpenApiExample(
                name="response",
                value=BRAND_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о конкретном бренде",
        summary="Обновление бренда",
        responses={200: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="request",
                value=REQUEST_EXAMPLE,
            ),
            OpenApiExample(
                name="response",
                value=BRAND_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частичное обновление информации о бренде",
        summary="Частичное обновление бренда",
        responses={200: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="Custom PATCH Request Example",
                request_only=True,
                value=PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на частичное обновление бренда для Swagger UI",
                summary="Пример запроса на частичное обновление бренда",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Custom PATCH Response Example",
                response_only=True,
                value=BRAND_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление бренда для Swagger UI",
                summary="Пример ответа на частичное обновление бренда",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить конкретный бренд",
        summary="Удаление бренда",
        responses={204: None},
        examples=[
            OpenApiExample(name="request", value=None),
            OpenApiExample(name="response", value=None),
        ],
    ),
)
@extend_schema(tags=["Shop"])
class BrandView(ModelViewSet):
    queryset = Brand.objects.order_by("-created_at")
    serializer_class = BrandSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
