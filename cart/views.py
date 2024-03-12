from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Sum

from rest_framework import status, permissions, viewsets, views
from rest_framework.response import Response
from rest_framework.decorators import action

from account.models import CustomUser
from cart.models import Order, ProductsInOrder, CartItem
from api.serializers import CartItemSerializer, OrderSerializer
from api.serializers import ProductDetailSerializer
from shop.models import Product

from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    tags=['Cart']
)
def add_to_cart(request):
    path = request.GET.get("next")

    if request.method == "POST":
        product_id = request.GET.get("product_id")

        if "cart" not in request.session:
            request.session["cart"] = {}

        cart = request.session.get("cart")

        if product_id in cart:
            cart[product_id]["quantity"] += 1

        else:
            cart[product_id] = {"quantity": 1}

    request.session.modified = True
    return redirect(path)


@extend_schema(
    tags=['Order']
)
class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        customer = request.user
        cart_items = CartItem.objects.filter(customer=customer)

        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста."}, status=status.HTTP_404_NOT_FOUND
            )

        with transaction.atomic():
            order = Order.objects.create(customer=customer)
            for item in cart_items:
                ProductsInOrder.objects.create(
                    order=order, product=item.product, quantity=item.quantity
                )
                item.delete()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Cart']
)
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Получить список всех элементов корзины",
        summary="Список элементов корзины",
        responses={200: CartItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "product": {
                            "id": 1,
                            "title": "Чердачная лестница Standard Termo",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "cherdachnaia-lestnitsa-standard-termo-5573",
                            "city_price": "4865",
                            "old_price": "3465",
                            "images": [
                                {
                                    "image_url": "catalog/products/facbff77-b636-46ba-83de-bc4be3fc7105.webp"
                                }
                            ],
                            "category_slug": "deke",
                        },
                        "quantity": 15,
                    },
                    {
                        "id": 2,
                        "product": {
                            "id": 2,
                            "title": "Хомут универсальный для водосточной трубы Standard, светло-коричневый",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                            "city_price": "6865",
                            "old_price": "3865",
                            "images": [
                                {
                                    "image_url": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"
                                }
                            ],
                            "category_slug": "deke",
                        },
                        "quantity": 12,
                    },
                ],
                description="Пример ответа для получения списка элементов корзины в Swagger UI",
                summary="Пример ответа для получения списка элементов корзины",
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "cartitemsdetail":
            return ProductDetailSerializer

        return super().get_serializer_class()

    @extend_schema(
        description="Добавить новые элементы в корзину",
        summary="Добавление новых элементов в корзину",
        responses={201: CartItemSerializer()},
        examples=[
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "product": {
                            "id": 3732,
                            "title": "Чердачная лестница Standard Termo",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "cherdachnaia-lestnitsa-standard-termo-5573",
                            "city_price": "4865",
                            "old_price": "3465",
                            "images": [
                                {
                                    "image_url": "catalog/products/facbff77-b636-46ba-83de-bc4be3fc7105.webp"
                                }
                            ],
                            "category_slug": "deke",
                        },
                        "quantity": 15,
                    },
                    {
                        "id": 2,
                        "product": {
                            "id": 3736,
                            "title": "Хомут универсальный для водосточной трубы Standard, светло-коричневый",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                            "city_price": "6865",
                            "old_price": "3865",
                            "images": [
                                {
                                    "image_url": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"
                                }
                            ],
                            "category_slug": "deke",
                        },
                        "quantity": 20,
                    },
                ],
                description="Пример ответа на добавление новых элементов в корзину в Swagger UI",
                summary="Пример ответа на добавление новых элементов в корзину",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        serializer = CartItemSerializer(
            data=request.data, many=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serialized_data = serializer.data
        return Response(serialized_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Получить информацию о конкретном элементе корзины",
        summary="Информация о элементе корзины",
        responses={200: ProductDetailSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value={
                    "id": 24,
                    "product": {
                        "id": 3732,
                        "title": "Желоб водосточный 3 м Premium, пломбир",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "image": "http://127.0.0.1:8000/media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-plombir-3732",
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp"
                            },
                        ],
                        "category_slug": "seriya-premium",
                    },
                    "quantity": 100,
                },
                description="Пример ответа для получения информации о конкретном элементе корзины в Swagger UI",
                summary="Пример ответа для получения информации о конкретном элементе корзины",
                media_type="application/json",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Получение подробной информации о товарах в корзине",
        summary="Получение подробной информации о товарах в корзине",
        responses={200: ProductDetailSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Get Detail Info Request Example",
                response_only=True,
                value=[
                    {
                        "id": 3732,
                        "category": {
                            "id": 132,
                            "name": "Серия Premium",
                            "slug": "seriya-premium",
                            "order": 15,
                            "parent": 128,
                            "children": ["Деке", "deke"],
                            "parents": [
                                ["Деке", "deke"],
                                ["Водосточные системы", "vodostochnyie-sistemyi"],
                            ],
                            "category_meta": [
                                {
                                    "title": "dummy title",
                                    "description": "dummy description ",
                                },
                            ],
                            "icon": "http://127.0.0.1:8000//media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp",
                            "image_url": "http://127.0.0.1:8000//media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp",
                            "is_visible": True,
                        },
                        "title": "Желоб водосточный 3 м Premium, пломбир",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "http://127.0.0.1:8000//media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-plombir-3732",
                        "created_at": "2024-03-11T13:45:13.024897+03:00",
                        "characteristic_values": [
                            {
                                "id": 89965,
                                "characteristic_name": "Выбранный цвет",
                                "value": "Пломбир (RAL 9003)",
                            },
                            {
                                "id": 89966,
                                "characteristic_name": "Вес брутто",
                                "value": "18.3 кг",
                            },
                        ],
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000//media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp"
                            },
                        ],
                    },
                    {
                        "id": 3733,
                        "category": {
                            "id": 132,
                            "name": "Серия Premium",
                            "slug": "seriya-premium",
                            "order": 15,
                            "parent": 128,
                            "children": [
                                ["Водосточные системы", "vodostochnyie-sistemyi"]
                            ],
                            "parents": [
                                ["Деке", "deke"],
                            ],
                            "category_meta": [
                                {
                                    "title": "dummy title",
                                    "description": "dummy description ",
                                },
                            ],
                            "icon": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "image_url": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                            "is_visible": True,
                        },
                        "title": "Желоб водосточный 3 м Premium, шоколад",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "http://127.0.0.1:8000//media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
                        "created_at": "2024-03-11T13:45:20.574851+03:00",
                        "characteristic_values": [
                            {
                                "id": 89977,
                                "characteristic_name": "Выбранный цвет",
                                "value": "Шоколад (RAL 8019)",
                            },
                            {
                                "id": 89978,
                                "characteristic_name": "Вес брутто",
                                "value": "18.3 кг",
                            },
                        ],
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                            },
                        ],
                    },
                ],
                description="Пример ответа подробной информации о товарах в корзине в Swagger UI",
                summary="Пример подробной информации о товарах в корзине",
                media_type="application/json",
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def cartitemsdetail(self, request):
        id_lists = list(
            CartItem.objects.filter(customer=request.user).values_list(
                "product", flat=True
            )
        )
        queryset = Product.objects.filter(id__in=id_lists)

        if queryset.exists():

            serialized_data = self.get_serializer(queryset, many=True).data

            return Response(serialized_data, status=status.HTTP_200_OK)

        return Response(
            {"message": "Cart items for user with pk %s not found" % request.user.pk},
            status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        description="Обновить информацию о конкретном элементе корзины",
        summary="Обновление информации о элементе корзины",
        responses={200: CartItemSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value={
                    "product_id": 3736,
                    "quantity": 20
                },
                description="Пример запроса на обновление информации о конкретном элементе корзины в Swagger UI",
                summary="Пример запроса на обновление информации о конкретном элементе корзины",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value={
                        "id": 2,
                        "product": {
                            "id": 3736,
                            "title": "Хомут универсальный для водосточной трубы Standard, светло-коричневый",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                            "city_price": "6865",
                            "old_price": "3865",
                            "images": [
                                {
                                    "image_url": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"
                                }
                            ],
                            "category_slug": "deke",
                        },
                        "quantity": 20,
                    },
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        description="Частично обновить информацию о конкретном элементе корзины",
        summary="Частичное обновление информации о элементе корзины",
        responses={200: ProductDetailSerializer()},
        examples=[
            OpenApiExample(
                name='Partial Update Request Example',
                request_only=True,
                value={
                    "quantity": 20,
                },
                description="Пример запроса на частичное обновление информации о конкретном элементе корзины в Swagger UI",
                summary="Пример запроса на частичное обновление информации о конкретном элементе корзины",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Partial Update Response Example',
                response_only=True,
                value={
                        "id": 2,
                        "product": {
                            "id": 3736,
                            "title": "Хомут универсальный для водосточной трубы Standard, светло-коричневый",
                            "brand": {
                                "id": 1,
                                "name": "Deke",
                                "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                                "order": 1,
                            },
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                            "city_price": "6865",
                            "old_price": "3865",
                            "images": [
                                {
                                    "image_url": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"
                                }
                            ],
                            "category_slug": "deke",
                        },
                        "quantity": 20,
                    },
                description="Пример ответа на частичное обновление информации о конкретном элементе корзины в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном элементе корзины",
                media_type="application/json",
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Удалить конкретный элемент из корзины",
        summary="Удаление элемента из корзины",
        responses={204: "No Content"},
        examples=[
            OpenApiExample(
                name='Delete Request Example',
                request_only=True,
                value=None,
                description="Удаление элемента из корзины"
            ),
            OpenApiExample(
                name='Delete Response Example',
                response_only=True,
                value=None,
                description="Удаление элемента из корзины"
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        # Returns only the cart items that belong to the current user.
        return CartItem.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        # Associates the new cart item with the current user.
        serializer.save(customer=self.request.user)


class CartCountView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Получение количества товаров в корзине для текущего пользователя",
        summary="Получение количества товаров в корзине для текущего пользователя",
        responses={200: "Success"},
        examples=[
            OpenApiExample(
                name='Get Count Response Example',
                response_only=True,
                value={
                    "count": 100
                },
                description="Получение количества товаров в корзине для текущего пользователя"
            )
        ]
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
            {"messsage": "Cart items for user with pk %s not found" % request.user.pk}
        )
