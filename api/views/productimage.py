from shop.models import ProductImage
from api.serializers import ProductImageSerializer

from rest_framework.viewsets import ModelViewSet
from api.permissions import ReadOnlyOrAdminPermission
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=["Shop"],
)
class ProductImageViewSet(ModelViewSet):
    queryset = ProductImage.objects.all()
    permission_classes = [
        ReadOnlyOrAdminPermission,
    ]
    serializer_class = ProductImageSerializer

    @extend_schema(
        summary="Создать новое изображение продукта",
        description="Эндпоинт для создания нового изображения продукта с указанием ID связанного продукта.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "product_id": 1,
                    "name": "example",
                    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value={
                    "id": 1,
                    "name": "example",
                    "thumb_img": "thumb_example.png",
                    "image_url": "/media/catalog/products/images/example.png",
                    "is_active": True,
                },
                response_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Получить изображения продуктов",
        description="Эндпоинт для получения всех изображений продуктов.",
        examples=[
            OpenApiExample(
                "Пример ответа",
                value=[
                    {
                        "id": 1,
                        "name": "Test",
                        "thumb_img": "фываыфафыв",
                        "image": "/media/catalog/products/images/image-70e50210-8678-4b3a-90f9-3626526c11cb.webp",
                        "is_active": True,
                    },
                    {
                        "id": 1,
                        "name": "Test",
                        "thumb_img": "фываыфафыв",
                        "image": "/media/catalog/products/images/image-70e50210-8678-4b3a-90f9-3626526c11cb.webp",
                        "is_active": True,
                    },
                ],
                response_only=True,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Получить одно изображение продукта",
        description="Эндпоинт для получения одного изображения продукта по его ID.",
        examples=[
            OpenApiExample(
                "Пример ответа",
                value={
                    "id": 1,
                    "name": "example",
                    "thumb_img": "thumb_example.png",
                    "image_url": "/media/catalog/products/images/example.png",
                    "is_active": True,
                },
                response_only=True,
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Обновить изображение продукта",
        description="Эндпоинт для обновления изображения продукта по его ID.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                value={
                    "product_id": 1,
                    "name": "updated_example",
                    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Пример ответа",
                value={
                    "id": 1,
                    "name": "updated_example",
                    "thumb_img": "thumb_example_updated.png",
                    "image": "/media/catalog/products/images/example_updated.png",
                    "is_active": True,
                },
                response_only=True,
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить изображение продукта",
        description="Эндпоинт для удаления изображения продукта по его ID.",
        examples=[
            OpenApiExample(
                "Пример ответа",
                value={"detail": "Изображение продукта успешно удалено."},
                response_only=True,
            ),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
