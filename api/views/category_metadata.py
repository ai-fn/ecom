from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.category_meta_data import CategoryMetaDataSerializer

from shop.models import CategoryMetaData
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=['Shop']
)
class CategoryMetaDataViewSet(viewsets.ModelViewSet):
    queryset = CategoryMetaData.objects.all().order_by("-created_at")
    serializer_class = CategoryMetaDataSerializer
    permission_classes = [ReadOnlyOrAdminPermission]


    @extend_schema(
        description="Получить список всех метаданных категорий",
        summary="Список метаданных категорий",
        responses={200: CategoryMetaDataSerializer(many=True)},
        examples=[
            OpenApiExample(
                name='List Response Example',
                response_only=True,
                value=[
                    {
                        "title": "Metadata 1",
                        "description": "Description 1",
                    },
                    {
                        "title": "Metadata 2",
                        "description": "Description 2",
                    },
                    # Добавьте другие метаданные категорий, если есть
                ],
                description="Пример ответа для получения списка всех метаданных категорий в Swagger UI",
                summary="Пример ответа для получения списка всех метаданных категорий",
                media_type="application/json",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретной метаданных категории",
        summary="Информация о метаданных категории",
        responses={200: CategoryMetaDataSerializer()},
        examples=[
            OpenApiExample(
                name='Retrieve Response Example',
                response_only=True,
                value={
                    "title": "Metadata 1",
                    "description": "Description 1",
                },
                description="Пример ответа для получения информации о конкретной метаданных категории в Swagger UI",
                summary="Пример ответа для получения информации о конкретной метаданных категории",
                media_type="application/json",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Создать новую метаданные категории",
        summary="Создание метаданных категории",
        request=CategoryMetaDataSerializer,
        responses={201: CategoryMetaDataSerializer()},
        examples=[
            OpenApiExample(
                name='Create Request Example',
                request_only=True,
                value={
                    "title": "New Metadata",
                    "description": "New Description"
                },
                description="Пример запроса на создание новой метаданных категории в Swagger UI",
                summary="Пример запроса на создание новой метаданных категории",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Create Response Example',
                response_only=True,
                value={
                    "title": "New Metadata",
                    "description": "New Description"
                },
                description="Пример ответа на создание новой метаданных категории в Swagger UI",
                summary="Пример ответа на создание новой метаданных категории",
                media_type="application/json",
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о метаданных категории",
        summary="Обновление метаданных категории",
        request=CategoryMetaDataSerializer,
        responses={200: CategoryMetaDataSerializer()},
        examples=[
            OpenApiExample(
                name='Update Request Example',
                request_only=True,
                value={
                    "title": "Updated Metadata",
                    "description": "Updated Description"
                },
                description="Пример запроса на обновление информации о метаданных категории в Swagger UI",
                summary="Пример запроса на обновление информации о метаданных категории",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Update Response Example',
                response_only=True,
                value={
                    "title": "Updated Metadata",
                    "description": "Updated Description"
                },
                description="Пример ответа на обновление информации о метаданных категории в Swagger UI",
                summary="Пример ответа на обновление информации о метаданных категории",
                media_type="application/json",
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о метаданных категории",
        summary="Частичное обновление метаданных категории",
        request=CategoryMetaDataSerializer,
        responses={200: CategoryMetaDataSerializer()},
        examples=[
            OpenApiExample(
                name='Partial Update Request Example',
                request_only=True,
                value={
                    "description": "Updated Description"
                },
                description="Пример запроса на частичное обновление информации о метаданных категории в Swagger UI",
                summary="Пример запроса на частичное обновление информации о метаданных категории",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Partial Update Response Example',
                response_only=True,
                value={
                    "title": "Updated Metadata",
                    "description": "Updated Description"
                },
                description="Пример ответа на частичное обновление информации о метаданных категории в Swagger UI",
                summary="Пример ответа на частичное обновление информации о метаданных категории",
                media_type="application/json",
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить метаданные категории",
        summary="Удаление метаданных категории",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
