from typing import List
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from api.permissions import ReadOnlyOrAdminPermission
from api.mixins import (
    ActiveQuerysetMixin,
    IntegrityErrorHandlingMixin,
    CacheResponse,
    DeleteSomeMixin,
)
from api.serializers import ProductFileSerializer
from shop.models import ProductFile

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)


PRPODUCT_FILE_REQUEST_EXAMPLE = {
    "file": "https://s3.aws.cloud/catalog/products/documents/20240301_142235.heic",
    "name": "Example file",
    "product": 5157,
}
PRODUCT_FILE_RESPONSE_EXAMPLE = {
    "id": 5,
    **PRPODUCT_FILE_REQUEST_EXAMPLE,
}

PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(PRPODUCT_FILE_REQUEST_EXAMPLE.items())[:2]
}


@extend_schema_view(
    list=extend_schema(
        summary="Список файлов продукта",
        description="Получить список файлов продукта",
        examples=[
            OpenApiExample(
                name="Response Example",
                value=PRODUCT_FILE_RESPONSE_EXAMPLE,
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Получение файла продукта",
        description="Получить существующий файл продукта по его ID",
        examples=[
            OpenApiExample(
                name="Response Example",
                value=PRODUCT_FILE_RESPONSE_EXAMPLE,
                response_only=True,
            )
        ],
    ),
    create=extend_schema(
        summary="Создание файла продукта",
        description="Создать новый файл продукта",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value=PRPODUCT_FILE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example",
                value=PRODUCT_FILE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Обновление файла продукта",
        description="Обновить существующий файл продукта",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value=PRPODUCT_FILE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example",
                value=PRODUCT_FILE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частичное обновление файла продукта",
        description="Частично обновить существующий файл продукта",
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value=PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                name="Response Example",
                value=PRODUCT_FILE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Удаление файла продукта",
        description="Удалить существующий файл продукта",
        examples=[
            OpenApiExample(
                name="Response Example",
                value={"detail": "Файл продукта успешно удален"},
                response_only=True,
            )
        ],
    ),
    delete_some=extend_schema(
        summary="Удаление нескольких файлов товара по id",
        description="Удаление нескольких файлов товара по id",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=ProductFileSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value={"detail": "'ids' field is required."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Пример запроса", request_only=True, value={"ids": [1, 2, 3]}
            ),
        ],
    ),
)
@extend_schema(tags=["api"])
class ProductFileViewSet(
    DeleteSomeMixin,
    ActiveQuerysetMixin,
    IntegrityErrorHandlingMixin,
    CacheResponse,
    ModelViewSet,
):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
