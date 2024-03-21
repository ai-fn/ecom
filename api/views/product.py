from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.product_catalog import ProductCatalogSerializer
from api.serializers.product_detail import ProductDetailSerializer
from shop.models import Category, Price, Product
from cart.models import CartItem
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.db.models import Q, Subquery, OuterRef
from rest_framework.response import Response
from rest_framework.decorators import action


@extend_schema(tags=["Shop"])
class ProductViewSet(viewsets.ModelViewSet):
    """
    Возвращает товары с учетом цены в заданном городе.
    """

    queryset = Product.objects.all().order_by("-created_at")
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductCatalogSerializer
        elif self.action == "productdetail":
            return ProductDetailSerializer
        return (
            ProductDetailSerializer  # Или какой-либо другой сериализатор по умолчанию
        )

    @extend_schema(
        description="Получить список всех продуктов в каталоге",
        summary="Получить список всех продуктов в каталоге",
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "title": "Product A",
                        "brand": 1,
                        "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "slug": "product-a",
                        "city_price": 100.0,
                        "old_price": 120.0,
                        "images": [
                            {
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-a",
                        "brand_slug": "brand-a",
                        "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    },
                    {
                        "id": 2,
                        "title": "Product B",
                        "brand": 2,
                        "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "slug": "product-b",
                        "city_price": 150.0,
                        "old_price": 110.0,
                        "images": [
                            {
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-b",
                        "brand_slug": "brand-a",
                        "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    },
                ],
            )
        ],
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для фильтрации цен",
            ),
            OpenApiParameter(
                name="price_gte",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Фильтр цены: больше или равно",
            ),
            OpenApiParameter(
                name="price_lte",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Фильтр цены: меньше или равно",
            ),
            OpenApiParameter(
                name="brand",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по бренду",
            ),
            OpenApiParameter(
                name="category",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по категории (slug)",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        city_domain = request.query_params.get("city_domain")
        price_lte = request.query_params.get("price_lte")
        price_gte = request.query_params.get("price_gte")
        brands = request.query_params.get("brand")
        category = request.query_params.get("category")

        filter_conditions = Q()

        if category:
            categories = [category]
            try:
                category_instance = Category.objects.get(slug=category)
            except Category.DoesNotExist:
                category_instance = None
            
            if category_instance:
                category_childrens = category_instance.get_descendants(
                    include_self=True
                ).values_list("slug", flat=True)
                categories.extend(category_childrens)

            filter_conditions &= Q(category__slug__in=categories) | Q(
                additional_categories__slug=category
            )

        if city_domain or price_gte or price_lte or brands:

            if city_domain:
                price_filter = Price.objects.filter(
                    product=OuterRef("pk"), city__domain=city_domain
                )

                if price_lte is not None:
                    price_filter = price_filter.filter(price__lte=price_lte)
                if price_gte is not None:
                    price_filter = price_filter.filter(price__gte=price_gte)

                filter_conditions &= Q(id__in=Subquery(price_filter.values("product")))

                self.queryset = self.queryset.annotate(
                    city_price=Subquery(price_filter.values("price")[:1]),
                    old_price=Subquery(price_filter.values("old_price")[:1]),
                )

            if brands:
                brands_list = brands.split(",")
                filter_conditions &= Q(brand__name__in=brands_list)

        filtered_queryset = self.queryset.filter(filter_conditions)
        if self.request.user.is_authenticated:

            # Вывод количества товара в корзине, если пользователь авторизован
            filtered_queryset.annotate(
                cart_quantity=Subquery(
                    CartItem.objects.filter(
                        customer=self.request.user, product=OuterRef("pk")
                    ).values("quantity")[:1]
                )
            )

        if not filtered_queryset.exists():
            return Response([])

        self.queryset = filtered_queryset

        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получение подробой информации о конкретном продукте",
        summary="Получение подробой информации о конкретном продукте",
        responses={200: ProductDetailSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "category": {
                        "id": 1,
                        "name": "New Name For Category A",
                        "slug": "new-name-for-category-a",
                        "order": 1,
                        "parent": 0,
                        "children": ["Водосточные системы", "vodostochnye-sistemy-2"],
                        "parents": ["Деке", "deke-1"],
                        "category_meta": [],
                        "category_meta_id": 0,
                        "icon": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "is_visible": True,
                    },
                    "category_id": 1,
                    "title": "Product A",
                    "brand": {
                        "id": 1,
                        "name": "Deke",
                        "icon": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                        "order": 1,
                        "slug": "brand-a",
                    },
                    "brand_id": 1,
                    "description": "Product description",
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "created_at": "2024-03-14T10:00:00Z",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "characteristic_values": [
                        {
                            "id": 1663,
                            "characteristic_name": "Выбранный цвет",
                            "value": "Шоколад (RAL 8019)",
                        },
                        {
                            "id": 1664,
                            "characteristic_name": "Вес брутто",
                            "value": "18.3 кг",
                        },
                    ],
                    "images": [
                        {
                            "id": 1,
                            "image_url": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                        },
                    ],
                },
                description="Пример ответа для получения подробой информации о конкретном продукте в Swagger UI",
                summary="Пример ответа для получения подробой информации о конкретном продукте",
                media_type="application/json",
            ),
        ],
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для получения цены товара",
            )
        ],
    )
    @action(detail=True, methods=["get"])
    def productdetail(self, request, pk=None):
        product = self.get_object()
        city_domain = request.query_params.get("city_domain")
        if city_domain:
            price_data = (
                Price.objects.filter(product=product, city__domain=city_domain)
                .values("price", "old_price")
                .first()
            )
            if price_data:
                product.city_price = price_data.get("price")
                product.old_price = price_data.get("old_price")

        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @extend_schema(
        description="Создать новый продукт в каталоге",
        summary="Создание нового продукта в каталоге",
        request=ProductCatalogSerializer,
        responses={201: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value={
                    "id": 1,
                    "title": "Product A",
                    "brand": 1,
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "in_stock": True,
                },
                description="Пример запроса на создание нового продукта в каталоге в Swagger UI",
                summary="Пример запроса на создание нового продукта в каталоге",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "title": "Product A",
                    "brand": 1,
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "in_stock": True,
                },
                description="Пример ответа на создание нового продукта в каталоге в Swagger UI",
                summary="Пример ответа на создание нового продукта в каталоге",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном продукте в каталоге",
        summary="Информация об отзыве",
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "title": "Product A",
                    "brand": 1,
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "in_stock": True,
                },
                description="Пример ответа для получения информации о конкретном продукте в каталоге в Swagger UI",
                summary="Пример ответа для получения информации о конкретном продукте в каталоге отзыве",
                media_type="application/json",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о продукте в каталоге",
        summary="Обновление информации о продукте в каталоге",
        request=ProductCatalogSerializer,
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value={
                    "title": "Updated Product Title",
                    "brand": 1,
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "in_stock": True,
                },
                description="Пример запроса на обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример запроса на обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "title": "Updated Product Title",
                    "brand": 1,
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "in_stock": True,
                },
                description="Пример ответа на обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример ответа на обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о продукте в каталоге",
        summary="Частичное обновление информации о продукте в каталоге",
        request=ProductCatalogSerializer,
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value={
                    "title": "Updated Product A",
                    "brand": 2,
                },
                description="Пример запроса на частичное обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример запроса на частичное обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "title": "Updated Product A",
                    "brand": 2,
                    "image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "image_url": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "catalog_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "search_image": "catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "in_stock": True,
                },
                description="Пример ответа на частичное обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример ответа на частичное обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        description="Удалить товар из каталога",
        summary="Удалить товар из каталога",
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
