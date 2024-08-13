from shop.models import ProductImage
from api.serializers import ProductImageSerializer

from rest_framework.viewsets import ModelViewSet
from api.permissions import ReadOnlyOrAdminPermission
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample


PRODUCT_IMAGE_REQUEST_EXAMPLE = {
    "name": "example",
    "thumb_img": "thumb_example.png",
    "image": "/media/catalog/products/images/example.png",
    "is_active": True,
}
PRODUCT_IMAGE_RESPONSE_EXAMPLE = {
    "id": 1,
    **PRODUCT_IMAGE_REQUEST_EXAMPLE,
}
PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(PRODUCT_IMAGE_REQUEST_EXAMPLE.items())[:2]
}

@extend_schema_view(
    list=extend_schema(
        summary="Получить изображения продуктов",
        description="Эндпоинт для получения всех изображений продуктов.",
        examples=[
            OpenApiExample(
                "Пример ответа",
                value=PRODUCT_IMAGE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Получить одно изображение продукта",
        description="Эндпоинт для получения одного изображения продукта по его ID.",
        examples=[
            OpenApiExample(
                "Пример ответа",
                value=PRODUCT_IMAGE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    create=extend_schema(
        summary="Создать новое изображение продукта",
        description="Эндпоинт для создания нового изображения продукта с указанием ID связанного продукта.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PRODUCT_IMAGE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value=PRODUCT_IMAGE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Обновить изображение продукта",
        description="Эндпоинт для обновления изображения продукта по его ID.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PRODUCT_IMAGE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value=PRODUCT_IMAGE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частично обновить изображение продукта",
        description="Частичное обновление изображения продукта по его ID.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                value=PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value=PRODUCT_IMAGE_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Удалить изображение продукта",
        description="Эндпоинт для удаления изображения продукта по его ID.",
        examples=[
            OpenApiExample(
                "Пример ответа",
                value={"detail": "Изображение продукта успешно удалено."},
                response_only=True,
            ),
        ],
    ),
)
@extend_schema(
    tags=["Shop"],
)
class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    permission_classes = [
        ReadOnlyOrAdminPermission,
    ]
    serializer_class = ProductImageSerializer
