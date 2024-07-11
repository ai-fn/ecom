from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from api.serializers import ProductFileSerializer
from shop.models import ProductFile

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(tags=["api"])
class ProductFileViewSet(ModelViewSet):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Список файлов продукта",
        description="Получить список файлов продукта",
        examples=[
            OpenApiExample(
                name="Response Example",
                value={
                    "count": 2,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 5,
                            "file": "/media/catalog/products/documents/20240301_142235.heic",
                            "name": "Test",
                            "is_active": True,
                            "product": 5158,
                        },
                        {
                            "id": 4,
                            "file": "/media/catalog/products/documents/20240301_142056.heic",
                            "name": "Test",
                            "is_active": True,
                            "product": 5157,
                        },
                    ],
                },
                response_only=True,
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создание файла продукта",
        description="Создать новый файл продукта",
        examples=[
            OpenApiExample(
                name="Request Example",
                value={
                    "file": "/media/catalog/products/documents/20240301_142235.heic",
                    "name": "Example file",
                    "product": 5157,
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example",
                value={
                    "id": 6,
                    "file": "/media/catalog/products/documents/20240301_142235.heic",
                    "name": "Example file",
                    "product": 5157,
                },
                response_only=True,
            )
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление файла продукта",
        description="Обновить существующий файл продукта",
        examples=[
            OpenApiExample(
                name="Request Example",
                value={
                    "file": "/media/catalog/products/documents/20240301_142235.heic",
                    "name": "Updated file",
                    "product": 5157,
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example",
                value={
                    "id": 6,
                    "file": "/media/catalog/products/documents/20240301_142235.heic",
                    "name": "Updated file",
                    "product": 5157,
                },
                response_only=True,
            )
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление файла продукта",
        description="Частично обновить существующий файл продукта",
        examples=[
            OpenApiExample(
                name="Request Example",
                value={
                    "name": "Partially updated file",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example",
                value={
                    "id": 6,
                    "file": "/media/catalog/products/documents/20240301_142235.heic",
                    "name": "Partially updated file",
                    "product": 5157,
                },
                response_only=True,
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление файла продукта",
        description="Удалить существующий файл продукта",
        examples=[
            OpenApiExample(
                name="Response Example",
                value={
                    "detail": "Файл продукта успешно удален"
                },
                response_only=True,
            )
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Получение файла продукта",
        description="Получить существующий файл продукта по его ID",
        examples=[
            OpenApiExample(
                name="Response Example",
                value={
                    "id": 6,
                    "file": "/media/catalog/products/documents/20240301_142235.heic",
                    "name": "Example file",
                    "product": 5157,
                },
                response_only=True,
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
