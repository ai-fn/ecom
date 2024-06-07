from rest_framework.viewsets import ModelViewSet
from api.serializers.products_in_order import ProductsInOrderSerializer
from rest_framework.permissions import IsAuthenticated
from cart.models import ProductsInOrder

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(tags=["Cart"])
class ProductsInOrderViewSet(ModelViewSet):
    queryset = ProductsInOrder.objects.all().order_by("-created_at")
    serializer_class = ProductsInOrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Получить список всех продуктов в заказе.",
        summary="Список продуктов в заказе",
        examples=[
            OpenApiExample(
                name="List Products in Order Example",
                value={
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
                    "id": 2,
                    "order": 1,
                    "product_id": 1,
                    "quantity": 15,
                    "price": "2.23",
                },
                description="Пример запроса для добавления нового продукта в заказ в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Product in Order Example",
                response_only=True,
                value={
                    "id": 1,
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
                description="Пример ответа на добавление нового продукта в заказ в Swagger UI",
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
                name="Пример запроса на обновление элемента заказа",
                request_only=True,
                value={
                    "order": 1,
                    "product_id": 11,
                    "quantity": 15,
                },
                description="Пример запроса для обновления информации о продукте в заказе в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Пример ответа на обновление элемента заказа",
                response_only=True,
                value={
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
                description="Пример ответа для обновления информации о продукте в заказе в Swagger UI",
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
            OpenApiExample(
                name="Пример частичного обновления элемента заказа",
                response_only=True,
                value={
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
                    "quantity": 3,
                    "price": "2.23",
                },
                description="Пример ответа для обновления информации о продукте в заказе в Swagger UI",
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
                name="Пример удаления элемента заказа",
                response_only=True,
                value=None,
                description="Пример ответа для удаления продукта из заказа в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
