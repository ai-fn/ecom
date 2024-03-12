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


# def view_cart(request):
#     path = request.GET.get('next')

#     context = {
#         'next': path,
#     }

#     cart = request.session.get('cart', None)

#     if cart:
#         products = {}
#         product_list = Product.objects.filter(pk__in=cart.keys()).values('id', 'title', 'description')

#         for product in product_list:
#             products[str(product['id'])] = product

#         for key in cart.keys():
#             cart[key]['product'] = products[key]

#         context['cart'] = cart

#     return render(request, 'cart/cart.html', context)


# @login_required(login_url='login')
# def view_order(request):
#     if request.method == 'POST':
#         user_id = request.user.pk
#         customer = CustomUser.objects.get(pk=user_id)

#         cart = request.session['cart']

#         if len(cart) > 0:
#             order = Order.objects.create(customer=customer)

#             for key, value in cart.items():
#                 product = Product.objects.get(pk=key)
#                 quantity = value['quantity']
#                 ProductsInOrder.objects.create(order=order, product=product, quantity=quantity)

#             request.session['cart'] = {}
#             request.session.modified = True

#             messages.success(request, 'Заказ принят')

#     return redirect('cart:cart')


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
                            "brand": 1,
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
                            "brand": 2,
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
                name="Create Request Example",
                request_only=True,
                value=[
                    {
                        "product_id": 3732,
                        "quantity": 15,
                    },
                    {
                        "product_id": 3736,
                        "quantity": 20,
                    },
                ],
                description="Пример запроса на добавление новых элементов в корзину в Swagger UI",
                summary="Пример запроса на добавление новых элементов в корзину",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "product": {
                            "id": 3732,
                            "title": "Чердачная лестница Standard Termo",
                            "brand": 1,
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "cherdachnaia-lestnitsa-standard-termo-5573",
                            "city_price": "4865",
                            "old_price": "3465",
                            "images": [{"image_url": "catalog/products/facbff77-b636-46ba-83de-bc4be3fc7105.webp"}],
                            "category_slug": "deke",
                        },
                        "quantity": 15,
                    },
                    {
                        "id": 2,
                        "product": {
                            "id": 3736,
                            "title": "Хомут универсальный для водосточной трубы Standard, светло-коричневый",
                            "brand": 2,
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                            "city_price": "6865",
                            "old_price":"3865",
                            "images": [{"image_url": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"}],
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
        description="Получение подробной информации о товаре в корзине",
        summary="Получение подробной информации о товаре в корзине",
        responses={200: ProductDetailSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=[
  {
    "id": 3732,
    "category": {
      "id": 132,
      "name": "Серия Premium",
      "slug": "seriya-premium",
      "order": 15,
      "parent": 128,
      "children": null,
      "parents": [
        [
          "Деке",
          "deke"
        ],
        [
          "Водосточные системы",
          "vodostochnyie-sistemyi"
        ]
      ],
      "category_meta": [],
      "icon": null,
      "image_url": null,
      "is_visible": true
    },
    "title": "Желоб водосточный 3 м Premium, пломбир",
    "brand": null,
    "description": "row['DESCRIPTION']",
    "image": null,
    "slug": "zhelob-vodostochnyi-3-m-premium-plombir-3732",
    "created_at": "2024-03-11T13:45:13.024897+03:00",
    "characteristic_values": [
      {
        "id": 89965,
        "characteristic_name": "Выбранный цвет",
        "value": "Пломбир (RAL 9003)"
      },
      {
        "id": 89966,
        "characteristic_name": "Вес брутто",
        "value": "18.3 кг"
      },
      {
        "id": 89967,
        "characteristic_name": "Выбранный цвет2",
        "value": "Пломбир (RAL 9003)"
      },
      {
        "id": 89968,
        "characteristic_name": "Кол-во в упаковке",
        "value": "10 шт"
      },
      {
        "id": 89969,
        "characteristic_name": "Тип упаковки",
        "value": "Полиэтилен"
      },
      {
        "id": 89970,
        "characteristic_name": "Толщина стенок",
        "value": "1.8 мм"
      },
      {
        "id": 89971,
        "characteristic_name": "Для кровли",
        "value": "150..250 м2"
      },
      {
        "id": 89972,
        "characteristic_name": "Глубина желоба",
        "value": "76 мм"
      },
      {
        "id": 89973,
        "characteristic_name": "Внешние размеры упаковки (ДхШхВ)",
        "value": "3000x130x130 мм"
      },
      {
        "id": 89974,
        "characteristic_name": "Длина",
        "value": "3 м"
      },
      {
        "id": 89975,
        "characteristic_name": "Ширина желоба",
        "value": "120.65 мм"
      },
      {
        "id": 89976,
        "characteristic_name": "Вес",
        "value": "1.91 кг"
      },
      {
        "id": 90075,
        "characteristic_name": "Выбранный цвет",
        "value": "Пломбир (RAL 9003)"
      },
      {
        "id": 90076,
        "characteristic_name": "Вес брутто",
        "value": "18.3 кг"
      },
      {
        "id": 90077,
        "characteristic_name": "Выбранный цвет2",
        "value": "Пломбир (RAL 9003)"
      },
      {
        "id": 90078,
        "characteristic_name": "Кол-во в упаковке",
        "value": "10 шт"
      },
      {
        "id": 90079,
        "characteristic_name": "Тип упаковки",
        "value": "Полиэтилен"
      },
      {
        "id": 90080,
        "characteristic_name": "Толщина стенок",
        "value": "1.8 мм"
      },
      {
        "id": 90081,
        "characteristic_name": "Для кровли",
        "value": "150..250 м2"
      },
      {
        "id": 90082,
        "characteristic_name": "Глубина желоба",
        "value": "76 мм"
      },
      {
        "id": 90083,
        "characteristic_name": "Внешние размеры упаковки (ДхШхВ)",
        "value": "3000x130x130 мм"
      },
      {
        "id": 90084,
        "characteristic_name": "Длина",
        "value": "3 м"
      },
      {
        "id": 90085,
        "characteristic_name": "Ширина желоба",
        "value": "120.65 мм"
      },
      {
        "id": 90086,
        "characteristic_name": "Вес",
        "value": "1.91 кг"
      }
    ],
    "images": [
      {
        "image_url": "http://127.0.0.1:8000/media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp"
      },
      {
        "image_url": "http://127.0.0.1:8000/media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp"
      }
    ]
  },
  {
    "id": 3733,
    "category": {
      "id": 132,
      "name": "Серия Premium",
      "slug": "seriya-premium",
      "order": 15,
      "parent": 128,
      "children": null,
      "parents": [
        [
          "Деке",
          "deke"
        ],
        [
          "Водосточные системы",
          "vodostochnyie-sistemyi"
        ]
      ],
      "category_meta": [],
      "icon": null,
      "image_url": null,
      "is_visible": true
    },
    "title": "Желоб водосточный 3 м Premium, шоколад",
    "brand": null,
    "description": "row['DESCRIPTION']",
    "image": null,
    "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-3733",
    "created_at": "2024-03-11T13:45:20.574851+03:00",
    "characteristic_values": [
      {
        "id": 89977,
        "characteristic_name": "Выбранный цвет",
        "value": "Шоколад (RAL 8019)"
      },
      {
        "id": 89978,
        "characteristic_name": "Вес брутто",
        "value": "18.3 кг"
      },
      {
        "id": 89979,
        "characteristic_name": "Выбранный цвет2",
        "value": "Шоколад (RAL 8019)"
      },
      {
        "id": 89980,
        "characteristic_name": "Кол-во в упаковке",
        "value": "10 шт"
      },
      {
        "id": 89981,
        "characteristic_name": "Тип упаковки",
        "value": "Полиэтилен"
      },
      {
        "id": 89982,
        "characteristic_name": "Толщина стенок",
        "value": "1.8 мм"
      },
      {
        "id": 89983,
        "characteristic_name": "Для кровли",
        "value": "150..250 м2"
      },
      {
        "id": 89984,
        "characteristic_name": "Глубина желоба",
        "value": "76 мм"
      },
      {
        "id": 89985,
        "characteristic_name": "Внешние размеры упаковки (ДхШхВ)",
        "value": "3000x130x130 мм"
      },
      {
        "id": 89986,
        "characteristic_name": "Длина",
        "value": "3 м"
      },
      {
        "id": 89987,
        "characteristic_name": "Ширина желоба",
        "value": "120.65 мм"
      },
      {
        "id": 89988,
        "characteristic_name": "Вес",
        "value": "1.91 кг"
      },
      {
        "id": 90087,
        "characteristic_name": "Выбранный цвет",
        "value": "Шоколад (RAL 8019)"
      },
      {
        "id": 90088,
        "characteristic_name": "Вес брутто",
        "value": "18.3 кг"
      },
      {
        "id": 90089,
        "characteristic_name": "Выбранный цвет2",
        "value": "Шоколад (RAL 8019)"
      },
      {
        "id": 90090,
        "characteristic_name": "Кол-во в упаковке",
        "value": "10 шт"
      },
      {
        "id": 90091,
        "characteristic_name": "Тип упаковки",
        "value": "Полиэтилен"
      },
      {
        "id": 90092,
        "characteristic_name": "Толщина стенок",
        "value": "1.8 мм"
      },
      {
        "id": 90093,
        "characteristic_name": "Для кровли",
        "value": "150..250 м2"
      },
      {
        "id": 90094,
        "characteristic_name": "Глубина желоба",
        "value": "76 мм"
      },
      {
        "id": 90095,
        "characteristic_name": "Внешние размеры упаковки (ДхШхВ)",
        "value": "3000x130x130 мм"
      },
      {
        "id": 90096,
        "characteristic_name": "Длина",
        "value": "3 м"
      },
      {
        "id": 90097,
        "characteristic_name": "Ширина желоба",
        "value": "120.65 мм"
      },
      {
        "id": 90098,
        "characteristic_name": "Вес",
        "value": "1.91 кг"
      }
    ],
    "images": [
      {
        "image_url": "http://127.0.0.1:8000/media/catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
      },
      {
        "image_url": "http://127.0.0.1:8000/media/catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
      }
    ]
  }
],
                description="Пример ответа подробной информации о товаре в корзине в Swagger UI",
                summary="Пример подробной информации о товаре в корзине",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "product": {
                            "id": 3732,
                            "title": "Чердачная лестница Standard Termo",
                            "brand": 1,
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "cherdachnaia-lestnitsa-standard-termo-5573",
                            "city_price": "4865",
                            "old_price": "3465",
                            "images": [{"image_url": "catalog/products/facbff77-b636-46ba-83de-bc4be3fc7105.webp"}],
                            "category_slug": "deke",
                        },
                        "quantity": 15,
                    },
                    {
                        "id": 2,
                        "product": {
                            "id": 3736,
                            "title": "Хомут универсальный для водосточной трубы Standard, светло-коричневый",
                            "brand": 2,
                            "image": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                            "city_price": "6865",
                            "old_price":"3865",
                            "images": [{"image_url": "catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"}],
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

    def get_queryset(self):
        # Returns only the cart items that belong to the current user.
        return CartItem.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        # Associates the new cart item with the current user.
        serializer.save(customer=self.request.user)


class CartCountView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]

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
