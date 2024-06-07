from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.brand import BrandSerializer
from shop.models import Brand
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(tags=["Shop"])
class BrandView(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех брендов",
        summary="Список брендов",
        responses={200: BrandSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="responce",
                value={
                    "id": 1,
                    "name": "Deke",
                    "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                    "order": 1,
                },
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Создать новый бренд",
        summary="Создание бренда",
        responses={201: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="request",
                value={
                    "name": "Deke",
                    "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                    "order": 1,
                },
            ),
            OpenApiExample(
                name="response",
                value={
                    "id": 1,
                    "name": "Deke",
                    "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                    "order": 1,
                },
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном бренде",
        summary="Информация о бренде",
        responses={200: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="response",
                value={
                    "id": 1,
                    "name": "Deke",
                    "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                    "order": 1,
                },
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о конкретном бренде",
        summary="Обновление бренда",
        responses={200: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="request",
                value={
                    "name": "Abba",
                    "icon": "category_icons/93235f40b-88f3-49a3-821c-6ba73126323b.webp",
                    "order": 5,
                },
            ),
            OpenApiExample(
                name="response",
                value={
                    "name": "Abba",
                    "icon": "category_icons/93235f40b-88f3-49a3-821c-6ba73126323b.webp",
                    "order": 5,
                },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить конкретный бренд",
        summary="Удаление бренда",
        responses={204: None},
        examples=[
            OpenApiExample(name="request", value=None),
            OpenApiExample(name="response", value=None),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="Частичное обновление информации о бренде",
        summary="Частичное обновление бренда",
        responses={200: BrandSerializer()},
        examples=[
            OpenApiExample(
                name="Custom PATCH Request Example",
                request_only=True,
                value={
                    "order": 2,
                },
                description="Пример запроса на частичное обновление бренда для Swagger UI",
                summary="Пример запроса на частичное обновление бренда",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Custom PATCH Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Abba",
                    "icon": "category_icons/93235f40b-88f3-49a3-821c-6ba73126323b.webp",
                    "order": 2,
                },
                description="Пример ответа на частичное обновление бренда для Swagger UI",
                summary="Пример ответа на частичное обновление бренда",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
