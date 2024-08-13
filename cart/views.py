from collections import defaultdict

from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from loguru import logger
from api.permissions import IsOwnerOrAdminPermission

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from bitrix_app.services import Bitrix24API
from cart.models import Order, ProductsInOrder, CartItem
from api.serializers import (
    CartItemSerializer,
    OrderSerializer,
    SimplifiedCartItemSerializer,
    ProductDetailSerializer,
)
from shop.models import Price, Product, ProductFrequenlyBoughtTogether
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, extend_schema_view
from api.views.products_in_order import PRODUCTS_IN_ORDER_RESPONSE_EXAMPLE
from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE, RETRIEVE_RESPONSE_EXAMPLE


ORDER_REQUEST_EXAMPLE = {
    "address": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
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


CART_ITEM_REQUEST_EXAMPLE = {
    "product_id": 1,
    "quantity": 20,
}
CART_ITEM_RESPONSE_EXAMPLE = {
    "id": 1,
    "product": UNAUTHORIZED_RESPONSE_EXAMPLE,
    "quantity": 20
}
CART_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(CART_ITEM_REQUEST_EXAMPLE.items())[:2]
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
class OrderViewSet(ModelViewSet):

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    bitrix_api = Bitrix24API()

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
        self.queryset = self.get_queryset().filter(is_active=True)
        return super().list(request, *args, **kwargs)


    def create(self, request, *args, **kwargs):
        total = 0
        city_domain = request.query_params.get("city_domain")
        data = dict(request.data)
        data["customer"] = request.user.pk

        cart_items = CartItem.objects.filter(customer=request.user.pk)

        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста."}, status=status.HTTP_404_NOT_FOUND
            )

        unavailable_products = (
            cart_items.prefetch_related("product")
            .filter(product__unavailable_in__domain=city_domain)
            .values_list("id", flat=True)
        )
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


@extend_schema_view(
    list=extend_schema(
        description="Получить список всех элементов корзины",
        summary="Список элементов корзины",
        responses={200: CartItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=CART_ITEM_RESPONSE_EXAMPLE,
                description="Пример ответа для получения списка элементов корзины в Swagger UI",
                summary="Пример ответа для получения списка элементов корзины",
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном элементе корзины",
        summary="Информация о элементе корзины",
        responses={200: ProductDetailSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=CART_ITEM_RESPONSE_EXAMPLE,
                description="Пример ответа для получения информации о конкретном элементе корзины в Swagger UI",
                summary="Пример ответа для получения информации о конкретном элементе корзины",
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Добавить новые элементы в корзину",
        summary="Добавление новых элементов в корзину",
        responses={201: CartItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=[CART_ITEM_REQUEST_EXAMPLE],
                description="Пример запроса на добавление новых элементов в корзину в Swagger UI",
                summary="Пример запроса на добавление новых элементов в корзину",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=[CART_ITEM_REQUEST_EXAMPLE],
                description="Пример ответа на добавление новых элементов в корзину в Swagger UI",
                summary="Пример ответа на добавление новых элементов в корзину",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о конкретном элементе корзины",
        summary="Обновление информации о элементе корзины",
        responses={200: CartItemSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=CART_ITEM_REQUEST_EXAMPLE,
                description="Пример запроса на обновление информации о конкретном элементе корзины в Swagger UI",
                summary="Пример запроса на обновление информации о конкретном элементе корзины",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value=CART_ITEM_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о конкретном элементе корзины",
        summary="Частичное обновление информации о элементе корзины",
        responses={200: ProductDetailSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value={
                    "quantity": 20,
                },
                description="Пример запроса на частичное обновление информации о конкретном элементе корзины в Swagger UI",
                summary="Пример запроса на частичное обновление информации о конкретном элементе корзины",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value=CART_ITEM_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление информации о конкретном элементе корзины в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном элементе корзины",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить конкретный элемент из корзины",
        summary="Удаление элемента из корзины",
        examples=[
            OpenApiExample(
                name="Delete Request Example",
                request_only=True,
                value=None,
                description="Удаление элемента из корзины",
            ),
            OpenApiExample(
                name="Delete Response Example",
                response_only=True,
                value=None,
                description="Удаление элемента из корзины",
            ),
        ],
    ),
    delete_cart=extend_schema(
        description="Удаление всех элементов из корзины",
        summary="Удаление всех элементов из корзины",
    ),
    delete_some=extend_schema(
        description="Удалить несколько товаров из корзины (необходимо передавать id товаров)",
        summary="Удалить несколько товаров из корзины",
        examples=[
            OpenApiExample(
                name="Delete Some Example",
                value={"products_id": [46, 47, 48]},
                request_only=True,
            ),
            OpenApiExample(
                name="Delete Some Example",
                response_only=True,
                value={"message": "Objects successfully deleted"},
                status_codes=[200],
            ),
            OpenApiExample(
                name="Delete Some Example",
                response_only=True,
                value={"message": "Nothing to delete"},
                status_codes=[400],
            ),
        ],
    ),
    get_simple_prods=extend_schema(
        description="Получить список минимальной информации об элементах корзины",
        summary="Список минимальной информации об элементах корзины",
        responses={200: SimplifiedCartItemSerializer()},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=[CART_ITEM_REQUEST_EXAMPLE],
                description="Пример ответа для получения списка минимальной информации об элементах корзины в Swagger UI",
                summary="Пример ответа для получения списка минимальной информации об элементах корзины",
                media_type="application/json",
            ),
        ],
    ),
    cartitems_detail=extend_schema(
        description="Получение подробной информации о товарах в корзине",
        summary="Получение подробной информации о товарах в корзине",
        responses={200: ProductDetailSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Get Detail Info Request Example",
                response_only=True,
                value=RETRIEVE_RESPONSE_EXAMPLE,
                description="Пример ответа подробной информации о товарах в корзине в Swagger UI",
                summary="Пример подробной информации о товарах в корзине",
                media_type="application/json",
            ),
        ],
    ),
    delete_by_prod=extend_schema(
        description="Delete Cart Item by Product ID",
        summary="Delete Cart Item by Product ID",
    ),
)
@extend_schema(
    tags=["Cart"],
    parameters=[
        OpenApiParameter(
            name="city_domain",
            description="Домен города",
            type=str,
            location=OpenApiParameter.QUERY,
        )
    ],
)
class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["city_domain"] = self.request.query_params.get("city_domain")
        return context


    def get_serializer_class(self):
        if self.action == "cartitems_detail":
            return ProductDetailSerializer
        elif self.action in ("partial_update", "get_simple_prods"):
            return SimplifiedCartItemSerializer

        return super().get_serializer_class()


    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


    def get_queryset(self):
        if self.action == "cartitems_detail":
            return self.queryset

        return self.queryset.filter(customer=self.request.user)


    @action(methods=["post"], detail=False)
    def delete_some(self, request, *args, **kwargs):
        ids_list = request.data.get("products_id", [])
        if not ids_list:
            return Response(
                {"message": "IDs is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.filter_queryset(self.get_queryset()).filter(
            product__in=ids_list
        )
        if not queryset:
            return Response(
                {"message": "Nothing to delete"}, status=status.HTTP_400_BAD_REQUEST
            )

        queryset.delete()
        return Response(
            {"message": "Objects successfully deleted"}, status=status.HTTP_200_OK
        )


    @action(methods=["delete"], detail=False)
    def delete_cart(self, request, *args, **kwargs):
        queryset = CartItem.objects.filter(customer=request.user)

        if queryset.exists():
            queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=["get"])
    def get_simple_prods(self, request, *args, **kwargs):
        queryset = CartItem.objects.filter(customer=request.user)
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Cart items for provided user not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )


    def create(self, request, *args, **kwargs):
        existing_cart_items = CartItem.objects.filter(customer=request.user)

        existing_cart_dict = {item.product.id: item for item in existing_cart_items}

        quantity_dict = defaultdict(int)
        for el in request.data:
            serializer = SimplifiedCartItemSerializer(data=el)
            serializer.is_valid(raise_exception=True)
            quantity_dict[serializer.data["product_id"]] += serializer.data["quantity"]

        unique_dict = [
            {"product_id": k, "quantity": v} for k, v in quantity_dict.items()
        ]
        for incoming_item in unique_dict:
            product_id = incoming_item["product_id"]
            new_quantity = incoming_item["quantity"]

            if product_id in existing_cart_dict:
                existing_item = existing_cart_dict[product_id]
                existing_item.quantity = new_quantity
                existing_item.save()
            else:
                CartItem.objects.create(
                    customer=request.user, product_id=product_id, quantity=new_quantity
                )

        updated_cart_items = CartItem.objects.filter(customer=request.user)
        response_serializer = SimplifiedCartItemSerializer(
            updated_cart_items, many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=["get"])
    def cartitems_detail(self, request, *args, **kwargs):
        id_lists = list(
            CartItem.objects.filter(customer=request.user).values_list(
                "product", flat=True
            )
        )
        self.queryset = Product.objects.filter(id__in=id_lists)
        return super().list(request, *args, **kwargs)


    def partial_update(self, request, *args, **kwargs):
        product_id = kwargs.get("pk")
        product = get_object_or_404(Product, id=product_id)
        cart_item = get_object_or_404(CartItem, product=product, customer=request.user)
        kwargs["pk"], self.kwargs["pk"] = cart_item.pk, cart_item.pk
        return super().partial_update(request, *args, **kwargs)


    @action(detail=True, methods=["delete"])
    def delete_by_prod(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        product = get_object_or_404(Product, pk=pk)
        cart_item = get_object_or_404(CartItem, product=product, customer=request.user)

        self.kwargs["pk"] = cart_item.pk
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["Cart"])
class CartCountView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    @extend_schema(
        description="Получение количества товаров в корзине для текущего пользователя",
        summary="Получение количества товаров в корзине для текущего пользователя",
        examples=[
            OpenApiExample(
                name="Get Count Response Example",
                response_only=True,
                value={
                    "count": 100,
                },
                description="Получение количества товаров в корзине для текущего пользователя",
            )
        ],
    )
    def get(self, request):
        queryset = CartItem.objects.filter(customer=request.user)
        if queryset.exists():
            return Response(
                {
                    "count": queryset.aggregate(total_quantity=Sum("quantity"))[
                        "total_quantity"
                    ]
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"messsage": f"Cart items for user with pk {request.user.pk} not found"}
        )
