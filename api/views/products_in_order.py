from rest_framework import viewsets
from api.serializers.products_in_order import ProductsInOrderSerializer
from rest_framework.permissions import IsAuthenticated
from cart.models import ProductsInOrder

from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    tags=['Cart']
)
class ProductsInOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductsInOrder.objects.all().order_by("-created_at")
    serializer_class = ProductsInOrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Получить список всех продуктов в заказе.",
        summary="Список продуктов в заказе",
        examples=[
            OpenApiExample(
                name="List Products in Order Example",
                value=[
                    {
                        "id": 1,
                        "order": 1,
                        "product": 1,
                        "quantity": 2,
                        "created_at": "2024-03-12T12:00:00Z",
                    },
                    # Добавьте другие продукты, если есть
                ],
                description="Пример ответа при запросе списка продуктов в заказе в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном продукте в заказе.",
        summary="Информация о продукте в заказе",
        examples=[
            OpenApiExample(
                name="Retrieve Product in Order Example",
                value={
                    "id": 1,
                    "order": 1,
                    "product": 1,
                    "quantity": 2,
                    "created_at": "2024-03-12T12:00:00Z",
                },
                description="Пример ответа при запросе информации о продукте в заказе в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Добавить новый продукт в заказ.",
        summary="Добавление продукта в заказ",
        request=ProductsInOrderSerializer,
        responses={201: ProductsInOrderSerializer},
        examples=[
            OpenApiExample(
                name="Create Product in Order Example",
                request_only=True,
                value={
                    "order": 1,
                    "product": 1,
                    "quantity": 2,
                },
                description="Пример запроса для добавления нового продукта в заказ в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о продукте в заказе.",
        summary="Обновление информации о продукте в заказе",
        request=ProductsInOrderSerializer,
        responses={200: ProductsInOrderSerializer},
        examples=[
            OpenApiExample(
                name="Update Product in Order Example",
                request_only=True,
                value={
                    "quantity": 3,
                },
                description="Пример запроса для обновления информации о продукте в заказе в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Частично обновить информацию о продукте в заказе.",
        summary="Частичное обновление информации о продукте в заказе",
        request=ProductsInOrderSerializer,
        responses={200: ProductsInOrderSerializer},
        examples=[
            OpenApiExample(
                name="Partial Update Product in Order Example",
                request_only=True,
                value={
                    "quantity": 3,
                },
                description="Пример запроса для частичного обновления информации о продукте в заказе в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить продукт из заказа.",
        summary="Удаление продукта из заказа",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Delete Product from Order Example",
                response_only=True,
                value=None,
                description="Пример ответа для удаления продукта из заказа в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
