
from django.db import transaction
from django.db.models import F
from loguru import logger

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse
from api.permissions import IsOwnerOrAdminPermission

from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from bitrix_app.services import Bitrix24API
from cart.models import Order, ProductsInOrder, CartItem
from api.serializers import (
    OrderSerializer,
    OrderSelectedSerializer,
)
from shop.models import Price, ProductFrequenlyBoughtTogether
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, extend_schema_view
from api.views.products_in_order import PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE


ORDER_REQUEST_EXAMPLE = {
    "delivery_type": "delivery",
    "receiver_first_name": "Иван",
    "receiver_last_name": "Петров",
    "receiver_phone": "+79996740923",
    "receiver_email": "example@mail.ru",
    "address": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
}
ORDER_SELECTED_ITEMS_REQUEST_EXAMPLE = {
    "cartitem_ids": [1, 2, 3, 4, 5],
    **ORDER_REQUEST_EXAMPLE,
}
ORDER_RESPONSE_EXAMPLE = {
    "id": 5,
    **ORDER_REQUEST_EXAMPLE,
    "customer": 1,
    "products": [PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE],
    "created_at": "2024-03-28T15:08:57.462177+03:00",
    "total": 137.66,
    "status": {"name": "Создан"},
}
ORDER_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    "customer": 1,
}

@extend_schema_view(
    list=extend_schema(
        description="Получить список всех заказов",
        summary="Список заказов",
        responses={200: OrderSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа для получения списка всех заказов в Swagger UI",
                summary="Пример ответа для получения списка всех заказов",
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном заказе",
        summary="Информация о заказе",
        responses={200: OrderSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа для получения информации о конкретном заказе в Swagger UI",
                summary="Пример ответа для получения информации о конкретном заказе",
                media_type="application/json",
            ),
        ],
    ),
    order_selected=extend_schema(
        description="Заказ выбранных товаров",
        summary="Заказ выбранных товаров",
        examples=[
            OpenApiExample(
                "Пример запроса",
                request_only=True,
                value={"cartitem_ids": [1, 2, 3], **ORDER_REQUEST_EXAMPLE},
            ),
            OpenApiExample(
                "Response Example",
                response_only=True,
                value=ORDER_RESPONSE_EXAMPLE,
            )
        ],
    ),
    create=extend_schema(
        description="Создать новый заказ",
        summary="Создание заказа",
        request=OrderSerializer,
        responses={201: OrderSerializer()},
        parameters=[
            OpenApiParameter(
                name="city_domain",
                description="Домен города",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
            )
        ],
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value={
                    "region": "Воронежская область",
                    "district": "Лискинский район",
                    "city_name": "Воронеж",
                    "street": "ул. Садовая",
                    "house": "101Б",
                },
                description="Пример запроса на создание нового заказа в Swagger UI",
                summary="Пример запроса на создание нового заказа",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа на создание нового заказа в Swagger UI",
                summary="Пример ответа ответа на создание нового заказа",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о конкретном заказе",
        summary="Обновление заказа",
        request=OrderSerializer,
        responses={200: OrderSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=ORDER_REQUEST_EXAMPLE,
                description="Пример запроса на обновление информации о конкретном заказе в Swagger UI",
                summary="Пример запроса на обновление информации о конкретном заказе",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value=ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа на обновление информации о конкретном заказе в Swagger UI",
                summary="Пример ответа на обновление информации о конкретном заказе",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о конкретном заказе",
        summary="Частичное обновление заказа",
        request=OrderSerializer,
        responses={200: OrderSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value={"customer": "2"},
                description="Пример запроса на частичное обновление информации о конкретном заказе в Swagger UI",
                summary="Пример запроса на частичное обновление информации о конкретном заказе",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value=ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление информации о конкретном заказе в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном заказе",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить заказ",
        summary="Удаление заказа",
        responses={204: None},
    ),
    active_orders=extend_schema(
        summary="Получение активных заказов пользователя",
        description="Получение активных заказов пользователя",
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=ORDER_RESPONSE_EXAMPLE,
                description="Пример ответа для получения списка всех заказов в Swagger UI",
                summary="Пример ответа для получения списка всех заказов",
                media_type="application/json",
            ),
        ],
    ),
)
@extend_schema(tags=["Order"])
class OrderViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    bitrix_api = Bitrix24API()

    def get_serializer_class(self):
        if self.action == "order_selected":
            return OrderSelectedSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAdminUser]
        elif self.action == "retrieve":
            self.permission_classes.append(IsOwnerOrAdminPermission)

        return super().get_permissions()


    def get_queryset(self):
        if self.action == "list":
            return super().get_queryset().filter(customer=self.request.user)

        return super().get_queryset()


    @action(detail=False, methods=["get"], url_path="active-orders")
    def active_orders(self, request, *args, **kwargs):
        self.queryset = self.get_queryset().exclude(status="DELIVERED")
        return super().list(request, *args, **kwargs)


    @action(detail=False, methods=["post"], url_path="order-selected")
    def order_selected(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        ids = serializer.validated_data.get("cartitem_ids")

        cart_items = CartItem.objects.select_related("product").filter(id__in=ids, customer=request.user.pk)
        if not cart_items.exists():
            return Response(
                {"error": "Элементы корзины с указанными id не найдены."}, status=status.HTTP_404_NOT_FOUND
            )

        return self.make_order(cart_items)

    def create(self, request, *args, **kwargs):

        cart_items = CartItem.objects.select_related("product").filter(customer=request.user.pk)
        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста."}, status=status.HTTP_404_NOT_FOUND
            )

        return self.make_order(cart_items)


    def make_order(self, cart_items):
        total = 0
        city_domain = self.request.query_params.get("city_domain")
        data = dict(self.request.data)
        data["customer"] = self.request.user.pk

        unavailable_products = cart_items.filter(product__unavailable_in__domain=city_domain).values_list("id", flat=True)
        if unavailable_products.exists():
            return Response(
                {
                    "detail": "Товары недоступны для заказа",
                    "cart_items": unavailable_products,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order = serializer.save()
            for item in cart_items:

                # Обновляем информацию о том, как часто покупают товар вместе с другими
                for other_item in cart_items.exclude(product__pk=item.product.pk):

                    friquenly_bought_together, _ = (
                        ProductFrequenlyBoughtTogether.objects.get_or_create(
                            product_from=item.product,
                            product_to=other_item.product,
                        )
                    )
                    friquenly_bought_together.purchase_count = F("purchase_count") + 1
                    friquenly_bought_together.save(update_fields=["purchase_count"])
                try:
                    price = Price.objects.get(
                        city_group__cities__domain=city_domain, product=item.product
                    )
                    prod = ProductsInOrder.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=price.price,
                    )
                except Exception as err:
                    logger.error(err)
                    order.delete()
                    return Response(
                        {"error": str(err)}, status=status.HTTP_400_BAD_REQUEST
                    )

                item.delete()
                total += prod.price * prod.quantity
                del prod
                del price

            order.total = total
            order.save(update_fields=["total"])

            self.bitrix_api.create_lead_for_order(order, city_domain)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

