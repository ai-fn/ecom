from rest_framework import viewsets
from api.serializers.order import OrderSerializer
from rest_framework.permissions import IsAuthenticated

from cart.models import Order
from drf_spectacular.utils import extend_schema, OpenApiExample


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


    @extend_schema(
        description="Получить информацию о конкретном заказе",
        summary="Информация о заказе",
        responses={200: OrderSerializer()},
        tags=['Orders'],
        examples=[
            OpenApiExample(
                name='Retrieve Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "customer": 1,
                    "products": [
                        {
                            "product_id": 101,
                            "quantity": 2
                        },
                        {
                            "product_id": 102,
                            "quantity": 1
                        }
                    ],
                    "created_at": "2024-03-12T12:00:00Z"
                },
                description="Пример ответа для получения информации о конкретном заказе в Swagger UI",
                summary="Пример ответа для получения информации о конкретном заказе",
                media_type="application/json",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создать новый заказ",
        summary="Создание заказа",
        responses={201: OrderSerializer()},
        tags=['Orders'],
        examples=[
            OpenApiExample(
                name='Create Request Example',
                request_only=True,
                value={
                    "customer": 1,
                    "products": [
                        {
                            "product_id": 104,
                            "quantity": 1
                        },
                        {
                            "product_id": 105,
                            "quantity": 2
                        }
                    ]
                },
                description="Пример запроса на создание нового заказа в Swagger UI",
                summary="Пример запроса на создание нового заказа",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Create Response Example',
                response_only=True,
                value={
                    "id": 3,
                    "customer": 1,
                    "products": [
                       {
                            "id": 0,
                            "order": 0,
                            "product": 0,
                            "quantity": 32767,
                            "created_at": "2024-03-12T12:32:54.080Z",
                        }
                    ],
                    "created_at": "2024-03-12T14:00:00Z"
                },
                description="Пример ответа на создание нового заказа в Swagger UI",
                summary="Пример ответа на создание нового заказа",
                media_type="application/json",
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


    @extend_schema(
        description="Частично обновить информацию о конкретном заказе",
        summary="Частично обновить информацию о конкретном заказе",
        responses={200: OrderSerializer()},
        tags=['Orders'],
        examples=[
            OpenApiExample(
                name='Partial Update Request Example',
                request_only=True,
                value={
                    "customer": 3,
                },
                description="Пример запроса на частичное обновление информации о конкретном заказе в Swagger UI",
                summary="Пример запроса на частичное обновление информации о конкретном заказе",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Partial Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "customer": 3,
                    "products": [
                        {
                            "product_id": 105,
                            "quantity": 5
                        }
                    ],
                    "created_at": "2024-03-12T12:00:00Z"
                },
                description="Пример ответа на частичное обновление информации о конкретном заказе в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном заказе",
                media_type="application/json",
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о конкретном заказе",
        summary="Обновление информации о заказе",
        responses={200: OrderSerializer()},
        tags=['Orders'],
        examples=[
            OpenApiExample(
                name='Update Request Example',
                request_only=True,
                value={
                    "customer": 2,
                    "products": [
                        {
                            "product_id": 105,
                            "quantity": 5
                        }
                    ]
                },
                description="Пример запроса на обновление информации о конкретном заказе в Swagger UI",
                summary="Пример запроса на обновление информации о конкретном заказе",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "customer": 2,
                    "products": [
                        {
                            "product_id": 105,
                            "quantity": 5
                        }
                    ],
                    "created_at": "2024-03-12T12:00:00Z"
                },
                description="Пример ответа на обновление информации о конкретном заказе в Swagger UI",
                summary="Пример ответа на обновление информации о конкретном заказе",
                media_type="application/json",
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Получить список всех заказов",
        summary="Список заказов",
        responses={200: OrderSerializer(many=True)},
        tags=['Orders'],
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                description="Пример ответа для получения списка заказов в Swagger UI",
                summary="Пример ответа для получения списка заказов",
                value=[
                    {
                        "cutomer": 1,
                        "products": [
                            {
                                "id": 0,
                                "order": 0,
                                "product": 0,
                                "quantity": 32767,
                                "created_at": "2024-03-12T12:32:54.080Z",
                            }
                        ],
                        "created_at": "2024-03-12T12:00:00Z",
                    },
                ],
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Удалить конкретный заказ",
        summary="Удаление заказа",
        responses={204: "No Content"},
        tags=['Orders'],
        examples=[
            OpenApiExample(
                name='Delete Request Example',
                request_only=True,
                value=None,
                description="Удаление заказа"
            ),
            OpenApiExample(
                name='Delete Response Example',
                response_only=True,
                value=None,
                description="Удаление заказа"
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
