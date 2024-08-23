from rest_framework.viewsets import ModelViewSet
from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.serializers.products_in_order import ProductsInOrderSerializer
from rest_framework.permissions import IsAuthenticated
from cart.models import ProductsInOrder

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample
from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE


PRODUCTS_IN_ORDER_REQUEST_EXAMPLE = {
    "order_id": 1,
    "product_id": 1,
    "quantity": 20,
    "price": 130.00
}
PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE = {
    "id": 2,
    "order": 1,
    "product": UNAUTHORIZED_RESPONSE_EXAMPLE,
    **PRODUCTS_IN_ORDER_REQUEST_EXAMPLE,
}
PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE.pop("product_id")
PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE.pop("order_id")

PRODUCTS_IN_ORDER_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(PRODUCTS_IN_ORDER_REQUEST_EXAMPLE.items())[:2]}


@extend_schema_view(
    list=extend_schema(
        description="Получить список всех продуктов в заказе.",
        summary="Список продуктов в заказе",
        responses={200: ProductsInOrderSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Products in Order Example",
                value=PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа при запросе списка продуктов в заказе в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном продукте в заказе.",
        summary="Информация о продукте в заказе",
        examples=[
            OpenApiExample(
                name="Retrieve Product in Order Example",
                value=PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа при запросе информации о продукте в заказе в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Добавить новый продукт в заказ.",
        summary="Добавление продукта в заказ",
        request=ProductsInOrderSerializer,
        responses={201: ProductsInOrderSerializer},
        examples=[
            OpenApiExample(
                name="Create Product in Order Example",
                request_only=True,
                value=PRODUCTS_IN_ORDER_REQUEST_EXAMPLE,
                description="Пример запроса для добавления нового продукта в заказ в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Product in Order Example",
                response_only=True,
                value=PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа на добавление нового продукта в заказ в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о продукте в заказе.",
        summary="Обновление информации о продукте в заказе",
        request=ProductsInOrderSerializer,
        responses={200: ProductsInOrderSerializer},
        examples=[
            OpenApiExample(
                name="Пример запроса на обновление элемента заказа",
                request_only=True,
                value=PRODUCTS_IN_ORDER_REQUEST_EXAMPLE,
                description="Пример запроса для обновления информации о продукте в заказе в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Пример ответа на обновление элемента заказа",
                response_only=True,
                value=PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа для обновления информации о продукте в заказе в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о продукте в заказе.",
        summary="Частичное обновление информации о продукте в заказе",
        request=ProductsInOrderSerializer,
        responses={200: ProductsInOrderSerializer},
        examples=[
            OpenApiExample(
                name="Partial Update Product in Order Example",
                request_only=True,
                value=PRODUCTS_IN_ORDER_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса для частичного обновления информации о продукте в заказе в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Пример частичного обновления элемента заказа",
                response_only=True,
                value=PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа для обновления информации о продукте в заказе в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить продукт из заказа.",
        summary="Удаление продукта из заказа",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Пример удаления элемента заказа",
                response_only=True,
                value=None,
                description="Пример ответа для удаления продукта из заказа в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
)
@extend_schema(tags=["Cart"])
class ProductsInOrderViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    queryset = ProductsInOrder.objects.order_by("-created_at")
    serializer_class = ProductsInOrderSerializer
    permission_classes = [IsAuthenticated]
