from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from api.permissions import IsOwner

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from cart.models import Order, ProductsInOrder, CartItem
from api.serializers import (
    CartItemSerializer,
    OrderSerializer,
    SimplifiedCartItemSerializer,
    ProductDetailSerializer,
)
from shop.models import Price, Product, ProductFrequenlyBoughtTogether
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter


@extend_schema(tags=["Order"])
class OrderViewSet(ModelViewSet):

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAdminUser]
        elif self.action == "retrieve":
            self.permission_classes.append(IsOwner)

        return super().get_permissions()

    def get_queryset(self):
        if self.action == "list":
            return super().get_queryset().filter(customer=self.request.user)

        return super().get_queryset()

    @extend_schema(
        description="Получить список всех заказов",
        summary="Список заказов",
        responses={200: OrderSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=[
                    {
                        "id": 5,
                        "customer": 1,
                        "products": [
                            {
                                "id": 2,
                                "order": 1,
                                "product": {
                                    "id": 11,
                                    "title": "Желоб водосточный 3 м Premium, шоколад",
                                    "brand": 1,
                                    "image": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp",
                                    "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                    "city_price": 74.87,
                                    "old_price": 74.87,
                                    "images": [
                                        {
                                            "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                        },
                                        {
                                            "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                        },
                                        {
                                            "image_url": "/media/catalog/products/image-288c5a83-dde5-4475-a059-3365811cce9e.webp"
                                        },
                                    ],
                                    "in_stock": True,
                                    "category_slug": "seriia-premium-3",
                                    "search_image": "/media/catalog/products/search-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                    "catalog_image": "/media/catalog/products/catalog-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                    "is_popular": False,
                                },
                                "quantity": 15,
                                "price": "2.23",
                            },
                            {
                                "id": 2,
                                "order": 1,
                                "product": {
                                    "id": 11,
                                    "title": "Желоб водосточный 3 м Premium, шоколад",
                                    "brand": 1,
                                    "image": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp",
                                    "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                    "city_price": 74.87,
                                    "old_price": 74.87,
                                    "images": [
                                        {
                                            "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                        },
                                        {
                                            "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                        },
                                        {
                                            "image_url": "/media/catalog/products/image-288c5a83-dde5-4475-a059-3365811cce9e.webp"
                                        },
                                    ],
                                    "in_stock": True,
                                    "category_slug": "seriia-premium-3",
                                    "search_image": "/media/catalog/products/search-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                    "catalog_image": "/media/catalog/products/catalog-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                    "is_popular": False,
                                },
                                "quantity": 15,
                                "price": "2.23",
                            },
                        ],
                        "created_at": "2024-03-28T15:08:57.462177+03:00",
                        "region": "Воронежская область",
                        "district": "",
                        "city_name": "Воронеж",
                        "street": "улица 20-летия Октября",
                        "house": "84",
                        "total": "137.66",
                        "status": {"name": "Создан"},
                    }
                ],
                description="Пример ответа для получения списка всех заказов в Swagger UI",
                summary="Пример ответа для получения списка всех заказов",
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном заказе",
        summary="Информация о заказе",
        responses={200: OrderSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value={
                    "id": 5,
                    "customer": 1,
                    "products": [
                        {
                            "id": 2,
                            "order": 1,
                            "product": {
                                "id": 11,
                                "title": "Желоб водосточный 3 м Premium, шоколад",
                                "brand": 1,
                                "image": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp",
                                "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                "city_price": 74.87,
                                "old_price": 74.87,
                                "images": [
                                    {
                                        "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-288c5a83-dde5-4475-a059-3365811cce9e.webp"
                                    },
                                ],
                                "in_stock": True,
                                "category_slug": "seriia-premium-3",
                                "search_image": "/media/catalog/products/search-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "catalog_image": "/media/catalog/products/catalog-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "is_popular": False,
                            },
                            "quantity": 15,
                            "price": "2.23",
                        },
                    ],
                    "created_at": "2024-03-28T15:08:57.462177+03:00",
                    "region": "Воронежская область",
                    "district": "",
                    "city_name": "Воронеж",
                    "street": "улица 20-летия Октября",
                    "house": "84",
                    "total": "137.66",
                    "status": {"name": "Создан"},
                },
                description="Пример ответа для получения информации о конкретном заказе в Swagger UI",
                summary="Пример ответа для получения информации о конкретном заказе",
                media_type="application/json",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
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
                value={
                    "id": 5,
                    "customer": 1,
                    "products": [
                        {
                            "id": 2,
                            "order": 1,
                            "product": {
                                "id": 11,
                                "title": "Желоб водосточный 3 м Premium, шоколад",
                                "brand": 1,
                                "image": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp",
                                "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                "city_price": 74.87,
                                "old_price": 74.87,
                                "images": [
                                    {
                                        "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-288c5a83-dde5-4475-a059-3365811cce9e.webp"
                                    },
                                ],
                                "in_stock": True,
                                "category_slug": "seriia-premium-3",
                                "search_image": "/media/catalog/products/search-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "catalog_image": "/media/catalog/products/catalog-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "is_popular": False,
                            },
                            "quantity": 15,
                            "price": "2.23",
                        },
                    ],
                    "created_at": "2024-03-28T15:08:57.462177+03:00",
                    "region": "Воронежская область",
                    "district": "",
                    "city_name": "Воронеж",
                    "street": "улица 20-летия Октября",
                    "house": "84",
                    "total": "137.66",
                    "status": {"name": "Создан"},
                },
                description="Пример ответа для получения информации о конкретном заказе в Swagger UI",
                summary="Пример ответа для получения информации о конкретном заказе",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        total = 0
        city_domain = request.query_params.get("city_domain")
        request.data["customer"] = request.user.pk
        cart_items = CartItem.objects.filter(customer=request.user.pk)

        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(data=request.data)
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

                price = Price.objects.get(
                    city__domain=city_domain, product=item.product
                )
                prod = ProductsInOrder.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=price.price,
                )

                item.delete()
                total += prod.price
                del prod
                del price

            order.total = total
            order.save(update_fields=["total"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Обновить информацию о конкретном заказе",
        summary="Обновление заказа",
        request=OrderSerializer,
        responses={200: OrderSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value={
                    "customer": 2,
                    "products": [
                        {
                            "id": 2,
                            "order": 1,
                            "product": {
                                "id": 2,
                                "order": 1,
                                "product": {
                                    "id": 11,
                                    "title": "Желоб водосточный 3 м Premium, шоколад",
                                    "brand": 1,
                                    "image": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp",
                                    "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                    "city_price": 74.87,
                                    "old_price": 74.87,
                                    "images": [
                                        {
                                            "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                        },
                                        {
                                            "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                        },
                                        {
                                            "image_url": "/media/catalog/products/image-288c5a83-dde5-4475-a059-3365811cce9e.webp"
                                        },
                                    ],
                                    "in_stock": True,
                                    "category_slug": "seriia-premium-3",
                                    "search_image": "/media/catalog/products/search-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                    "catalog_image": "/media/catalog/products/catalog-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                    "is_popular": False,
                                },
                                "quantity": 15,
                                "price": "2.23",
                            },
                            "quantity": 15,
                            "price": "2.23",
                        },
                    ],
                    "created_at": "2024-03-28T15:08:57.462177+03:00",
                    "region": "Воронежская область",
                    "district": "",
                    "city_name": "Воронеж",
                    "street": "улица 20-летия Октября",
                    "house": "84",
                    "total": "137.66",
                    "status": {"name": "Создан"},
                },
                description="Пример запроса на обновление информации о конкретном заказе в Swagger UI",
                summary="Пример запроса на обновление информации о конкретном заказе",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value={
                    "id": 5,
                    "customer": 2,
                    "products": [
                        {
                            "id": 2,
                            "order": 1,
                            "product": {
                                "id": 11,
                                "title": "Желоб водосточный 3 м Premium, шоколад",
                                "brand": 1,
                                "image": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp",
                                "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                "city_price": 74.87,
                                "old_price": 74.87,
                                "images": [
                                    {
                                        "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-288c5a83-dde5-4475-a059-3365811cce9e.webp"
                                    },
                                ],
                                "in_stock": True,
                                "category_slug": "seriia-premium-3",
                                "search_image": "/media/catalog/products/search-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "catalog_image": "/media/catalog/products/catalog-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "is_popular": False,
                            },
                            "quantity": 15,
                            "price": "2.23",
                        },
                    ],
                    "created_at": "2024-03-28T15:08:57.462177+03:00",
                    "region": "Воронежская область",
                    "district": "",
                    "city_name": "Воронеж",
                    "street": "улица 20-летия Октября",
                    "house": "84",
                    "total": "137.66",
                    "status": {"name": "Создан"},
                },
                description="Пример ответа на обновление информации о конкретном заказе в Swagger UI",
                summary="Пример ответа на обновление информации о конкретном заказе",
                media_type="application/json",
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
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
                value={
                    "id": 5,
                    "customer": 2,
                    "products": [
                        {
                            "id": 2,
                            "order": 1,
                            "product": {
                                "id": 11,
                                "title": "Желоб водосточный 3 м Premium, шоколад",
                                "brand": 1,
                                "image": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp",
                                "slug": "zhelob-vodostochnyi-3-m-premium-shokolad-11",
                                "city_price": 74.87,
                                "old_price": 74.87,
                                "images": [
                                    {
                                        "image_url": "/media/catalog/products/image-476565d5-b3aa-494f-8e57-a8c92af898cb.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-4b7bec97-73e4-43ab-ae1e-17612fb6d2e8.webp"
                                    },
                                    {
                                        "image_url": "/media/catalog/products/image-288c5a83-dde5-4475-a059-3365811cce9e.webp"
                                    },
                                ],
                                "in_stock": True,
                                "category_slug": "seriia-premium-3",
                                "search_image": "/media/catalog/products/search-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "catalog_image": "/media/catalog/products/catalog-image-288c5a83-dde5-4475-a059-3365811cce9e.webp",
                                "is_popular": False,
                            },
                            "quantity": 15,
                            "price": "2.23",
                        },
                    ],
                    "created_at": "2024-03-28T15:08:57.462177+03:00",
                    "region": "Воронежская область",
                    "district": "",
                    "city_name": "Воронеж",
                    "street": "улица 20-летия Октября",
                    "house": "84",
                    "total": "137.66",
                    "status": {"name": "Создан"},
                },
                description="Пример ответа на частичное обновление информации о конкретном заказе в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном заказе",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить заказ",
        summary="Удаление заказа",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=["Cart"])
class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {})
        kwargs["context"]["city_domain"] = getattr(self, "city_domain", "")
        kwargs["context"]["request"] = self.request
        return super().get_serializer(*args, **kwargs)

    @extend_schema(
        description="Получить список всех элементов корзины",
        summary="Список элементов корзины",
        responses={200: CartItemSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name="city_domain",
                description="Домен города",
                type=str,
                location=OpenApiParameter.QUERY,
            )
        ],
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
                            "image": "/media/catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "cherdachnaia-lestnitsa-standard-termo-5573",
                            "city_price": "4865",
                            "old_price": "3465",
                            "images": [
                                {
                                    "image_url": "/media/catalog/products/facbff77-b636-46ba-83de-bc4be3fc7105.webp"
                                }
                            ],
                            "category_slug": "deke",
                            "brand_slug": "test_brand-1",
                            "search_image": "http://127.0.0.1:8000catalog/products/search-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
                            "catalog_image": "http://127.0.0.1:8000catalog/products/catalog-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
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
                            "image": "/media/catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                            "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                            "images": [
                                {
                                    "image_url": "/media/catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"
                                }
                            ],
                            "category_slug": "deke",
                            "brand_slug": "test_brand-1",
                            "search_image": "http://127.0.0.1:8000catalog/products/search-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
                            "catalog_image": "http://127.0.0.1:8000catalog/products/catalog-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
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

        self.city_domain = request.query_params.get("city_domain")

        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Удалить несколько товаров из корзины",
        summary="Удалить несколько товаров из корзины",
        examples=[
            OpenApiExample(
                name="Delete Some Example",
                value={"ids": [46, 47, 48]},
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
    )
    @action(methods=["post"], detail=False)
    def delete_some(self, request, *args, **kwargs):
        ids_list = request.data.get("ids", [])
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

    @extend_schema(
        description="Удаление всех элементов из корзины",
        summary="Удаление всех элементов из корзины",
    )
    @action(methods=["delete"], detail=False)
    def delete_cart(self, request, *args, **kwargs):
        queryset = CartItem.objects.filter(customer=request.user)

        if queryset.exists():
            queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == "cartitems_detail":
            return ProductDetailSerializer
        elif self.action == "partial_update":
            return SimplifiedCartItemSerializer
        elif self.action == "get_simple_prods":
            return SimplifiedCartItemSerializer

        return super().get_serializer_class()

    @extend_schema(
        description="Получить список минимальной информации об элементах корзины",
        summary="Список минимальной информации об элементах корзины",
        responses={200: SimplifiedCartItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=[
                    {
                        "product_id": 1,
                        "quantity": 15,
                    },
                    {
                        "product_id": 2,
                        "quantity": 12,
                    },
                ],
                description="Пример ответа для получения списка минимальной информации об элементах корзины в Swagger UI",
                summary="Пример ответа для получения списка минимальной информации об элементах корзины",
                media_type="application/json",
            ),
        ],
    )
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

    @extend_schema(
        description="Добавить новые элементы в корзину",
        summary="Добавление новых элементов в корзину",
        responses={201: CartItemSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=[
                    {"product_id": 3732, "quantity": 15},
                    {"product_id": 3733, "quantity": 13},
                ],
                description="Пример запроса на добавление новых элементов в корзину в Swagger UI",
                summary="Пример запроса на добавление новых элементов в корзину",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=[
                    {"product_id": 3732, "quantity": 15},
                    {"product_id": 3733, "quantity": 13},
                ],
                description="Пример ответа на добавление новых элементов в корзину в Swagger UI",
                summary="Пример ответа на добавление новых элементов в корзину",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        # Get current user's cart items
        existing_cart_items = CartItem.objects.filter(customer=request.user)

        # Transform existing cart items into a dictionary using product_id for easier processing
        existing_cart_dict = {item.product.id: item for item in existing_cart_items}

        # Process incoming data
        for incoming_item in request.data:
            product_id = incoming_item.get("product_id")
            new_quantity = incoming_item.get("quantity", 0)

            # Update existing item or create a new one
            if product_id in existing_cart_dict:
                # Update quantity of existing item
                existing_item = existing_cart_dict[product_id]
                existing_item.quantity = new_quantity  # Add to the existing quantity
                existing_item.save()
            else:
                # Create a new cart item for this user
                CartItem.objects.create(
                    customer=request.user, product_id=product_id, quantity=new_quantity
                )

        # After updating the cart, return the updated cart items for the user
        updated_cart_items = CartItem.objects.filter(customer=request.user)
        response_serializer = SimplifiedCartItemSerializer(
            updated_cart_items, many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

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
                        "image": "http://127.0.0.1:8000catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp",
                        "slug": "zhelob-vodostochnyi-3-m-premium-plombir-3732",
                        "images": [
                            {
                                "image_url": "http://127.0.0.1:8000catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp"
                            },
                        ],
                        "category_slug": "seriya-premium",
                        "brand_slug": "test_brand-1",
                        "search_image": "http://127.0.0.1:8000catalog/products/search-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
                        "catalog_image": "http://127.0.0.1:8000catalog/products/catalog-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
                        "is_stock": True,
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
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 2,
                            "children": 2,
                            "parents": ["Деке", "deke-1"],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description",
                                }
                            ],
                            "category_meta_id": 1,
                            "icon": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "image_url": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "is_visible": True,
                            "is_popular": False,
                        },
                        "title": "Желоб водосточный 3 м Premium, пломбир",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "/media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp",
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
                                "image_url": "/media/catalog/products/a42d0139-f06b-462a-bd70-4885d7edc288.webp"
                            },
                            {
                                "image_url": "/media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp"
                            },
                        ],
                        "in_stock": True,
                    },
                    {
                        "id": 3733,
                        "category": {
                            "id": 1,
                            "name": "Category A",
                            "slug": "category-a",
                            "order": 1,
                            "parent": 2,
                            "children": 2,
                            "parents": ["Деке", "deke-1"],
                            "category_meta": [
                                {
                                    "title": "dummy-title",
                                    "description": "dummy-description",
                                }
                            ],
                            "category_meta_id": 1,
                            "icon": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "image_url": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
                            "is_visible": True,
                            "is_popular": False,
                        },
                        "title": "Желоб водосточный 3 м Premium, шоколад",
                        "brand": {
                            "id": 1,
                            "name": "Deke",
                            "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                            "order": 1,
                        },
                        "description": "Желоб водосточный 3 м Premium, пломбир",
                        "image": "/media/catalog/products/35533f8a-48bb-462a-b1d9-1e57b6ca10e7.webp",
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
                                "image_url": "http://127.0.0.1:8000catalog/products/f09e1871-915e-4653-9a0d-68415f4eccec.webp"
                            },
                            {
                                "image_url": "http://127.0.0.1:8000catalog/products/bd312a69-ed3b-4f43-b4bb-45456ef1b48e.webp"
                            },
                        ],
                        "in_stock": True,
                    },
                ],
                description="Пример ответа подробной информации о товарах в корзине в Swagger UI",
                summary="Пример подробной информации о товарах в корзине",
                media_type="application/json",
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def cartitems_detail(self, request):
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
            {"message": f"Cart items for user with pk {request.user.pk} not found"},
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
                value={"product_id": 3736, "quantity": 20},
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
                        "image": "/media/catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                        "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                        "city_price": "6865",
                        "old_price": "3865",
                        "images": [
                            {
                                "image_url": "/media/catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"
                            }
                        ],
                        "category_slug": "deke",
                        "brand_slug": "test_brand-1",
                        "search_image": "http://127.0.0.1:8000catalog/products/search-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
                        "catalog_image": "http://127.0.0.1:8000catalog/products/catalog-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
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
                        "image": "/media/catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp",
                        "slug": "khomut-universalnyi-dlia-vodostochnoi-truby-standard-svetlo-korichnevyi-5560",
                        "city_price": "6865",
                        "old_price": "3865",
                        "images": [
                            {
                                "image_url": "/media/catalog/products/edc6eea5-7202-44d6-8e76-a7bbdc5c16ce.webp"
                            }
                        ],
                        "category_slug": "deke",
                        "brand_slug": "test_brand-1",
                        "search_image": "http://127.0.0.1:8000catalog/products/search-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
                        "catalog_image": "http://127.0.0.1:8000catalog/products/catalog-image-4ae4f533-785b-465b-ad46-e2fd9e459660.webp",
                    },
                    "quantity": 20,
                },
                description="Пример ответа на частичное обновление информации о конкретном элементе корзины в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретном элементе корзины",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        # Получаем product_id из URL-шаблона
        product_id = kwargs.get("pk")
        # Получаем объект Product или возвращаем 404, если он не найден
        product = get_object_or_404(Product, id=product_id)
        # Получаем объект CartItem, связанный с этим Product, или создаем новый
        cart_item = get_object_or_404(CartItem, product=product, customer=request.user)
        # Передаем управление стандартному методу partial_update, передавая cart_item вместо kwargs['pk']
        kwargs["pk"], self.kwargs["pk"] = cart_item.pk, cart_item.pk
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
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
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="Delete Cart Item by Product ID",
        summary="Delete Cart Item by Product ID",
    )
    @action(detail=True, methods=["delete"])
    def delete_by_prod(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        product = get_object_or_404(Product, pk=pk)
        cart_item = get_object_or_404(CartItem, product=product, customer=request.user)

        self.kwargs["pk"] = cart_item.pk
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        # Returns only the cart items that belong to the current user.
        return self.queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        # Associates the new cart item with the current user.
        serializer.save(customer=self.request.user)


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
                value={"count": 100},
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
