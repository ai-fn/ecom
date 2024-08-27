from django.db.models import F, Sum, Prefetch, Q
from django_filters import rest_framework as filters

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.serializers.brand import BrandSerializer
from shop.models import Brand, Category, CharacteristicValue, Price, Product, Characteristic, Review

from api.filters import ProductFilter
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import CharacteristicFilterSerializer
from api.serializers import ProductCatalogSerializer
from api.serializers import ProductDetailSerializer
from api.views.category import CATEGORY_RESPONSE_EXAMPLE
from api.views.brand import BRAND_RESPONSE_EXAMPLE
from api.views.productimage import PRODUCT_IMAGE_RESPONSE_EXAMPLE
from api.views.productfile import PRODUCT_FILE_RESPONSE_EXAMPLE

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action


BASE_PRODUCT_RESPONSE = {
    "id": 4883,
    "title": "TEST PRODUCT 2",
    "brand": 1,
    "h1_tag": "dummy-h1-tag",
    "article": "dummy-article",
    "slug": "test-product-4883",
    "city_price": 120.00,
    "old_price": 130.00,
    "category_slug": "krovelnye-materialy",
    "brand_slug": "tekhnonikol",
    "search_image": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
    "catalog_image": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
    "original_image": "/media/catalog/products/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.webp",
    "thumb_img": "dkjfdkfhkjshgfjkehskfbhjkasldewhefbcsdhecgfbhsewlfgbcsekhfesfdbvslhefglsefghdjlsehfcdegcsdjeu",
    "description": "TEST PRODUCT 2 TEST PRODUCT 2 TEST PRODUCT 2 TEST PRODUCT 2 TEST PRODUCT 2",
    "priority": 500,
    "is_popular": False,
    "is_new": False,
    "in_promo": False,
    "is_active": True,
    "in_stock": True,
    "rating": 4.0,
    "reviews_count": 10,
}

UNAUTHORIZED_RESPONSE_EXAMPLE = {
    **BASE_PRODUCT_RESPONSE,
    "images": [PRODUCT_IMAGE_RESPONSE_EXAMPLE],
}

AUTHORIZED_RESPONSE_EXAMPLE = {
    **UNAUTHORIZED_RESPONSE_EXAMPLE,
    "cart_quantity": 20,
}

UPDATE_REQUEST_EXAMPLE = {
    "h1_tag": "dummy-h1-tag",
    "category": 1,
    "title": "dummy-title",
    "brand": 1,
    "article": "dummy-article",
    "description": "dummy-description",
    "slug": "dummy-slug",
    "characteristic_values": [
        {
            "characteristic_id": 12,
            "product_id": 13,
            "value": (
                "Применяется для защиты теплоизоляционного слоя и внутренних элементов "
                "конструкции стен от ветра."
            ),
        },
    ],
    "images": [PRODUCT_IMAGE_RESPONSE_EXAMPLE],
    "in_stock": True,
    "is_popular": False,
    "is_new": True,
    "thumb_img": "base64string",
    "is_active": True,
}

PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    key: UPDATE_REQUEST_EXAMPLE[key]
    for key in ["h1_tag", "category"]
}

RETRIEVE_RESPONSE_EXAMPLE = {
    "id": 5138,
    **UPDATE_REQUEST_EXAMPLE,
    "category": CATEGORY_RESPONSE_EXAMPLE,
    "brand": BRAND_RESPONSE_EXAMPLE,
    "created_at": "2024-06-04T16:57:46.221822+03:00",
    "city_price": 120.00,
    "old_price": 130.00,
    "priority": 500,
    "rating": 4.0,
    "reviews_count": 10,
    "files": [PRODUCT_FILE_RESPONSE_EXAMPLE],
    "groups": {
        "visual_groups": [
            {
                "id": 1,
                "characteristic": "dummy-characteristic-name",
                "products": [
                    {
                        "id": 1,
                        "title": "dummy-title",
                        "slug": "dummy-slug",
                        "category_slug": "dummy-category-slug",
                        "characteristics": [
                            {
                                "id": 1,
                                "value": "dummy-value",
                                "characteristic__name": "dummy-name",
                            }
                        ],
                        "is_selected": False,
                    }
                ],
                "category_image": "/media/catalog/products/images/dummy-image.webp",
            },
        ],
        "non_visual_group": [
            {
                "id": 1,
                "characteristic": "dummy-characteristic-name",
                "products": [
                    {
                        "id": 1,
                        "title": "dummy-title",
                        "slug": "dummy-slug",
                        "category_slug": "dummy-category-slug",
                        "characteristics": [
                            {
                                "id": 1,
                                "value": "dummy-value",
                                "characteristic__name": "dummy-name",
                            }
                        ],
                        "is_selected": False,
                    }
                ]
            }
        ],
    }
}
RETRIEVE_RESPONSE_EXAMPLE.pop("characteristic_values")


@extend_schema(tags=["Shop"])
@extend_schema_view(
    frequenly_bought=extend_schema(
        description="Список товаров, которые часто покупают вместе с переданным",
        summary="Список товаров, которые часто покупают вместе с переданным",
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для фильтрации цен",
            ),
        ],
        examples=[
            OpenApiExample(
                name="Unauthorized Response Example",
                response_only=True,
                value=UNAUTHORIZED_RESPONSE_EXAMPLE,
            ),
            OpenApiExample(
                name="Authorized Response Example",
                response_only=True,
                value=AUTHORIZED_RESPONSE_EXAMPLE,
            ),
        ],
    ),
    popular_products=extend_schema(
        description="Получение популярных товаров",
        summary="Получение популярных товаров",
        examples=[
            OpenApiExample(
                name="Unauthorized Response Example",
                response_only=True,
                value=UNAUTHORIZED_RESPONSE_EXAMPLE,
            ),
            OpenApiExample(
                name="Authorized Response Example",
                response_only=True,
                value=AUTHORIZED_RESPONSE_EXAMPLE,
            ),
        ],
        parameters=[
            OpenApiParameter(
                name="city_domain",
                description="Домен города",
                type=str,
                default="msk.krov.market",
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
    ),
    list=extend_schema(
        description="Получить список всех продуктов в каталоге",
        summary="Получить список всех продуктов в каталоге",
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Unauthorized Response Example",
                response_only=True,
                value=UNAUTHORIZED_RESPONSE_EXAMPLE,
            ),
            OpenApiExample(
                name="Authorized Response Example",
                response_only=True,
                value=AUTHORIZED_RESPONSE_EXAMPLE,
            ),
        ],
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для фильтрации цен",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Параметр для поиска",
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
                name="brand_slug",
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
            OpenApiParameter(
                name="brand_filter",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по нескольким брендам (slug)",
            ),
        ],
    ),
    productdetail=extend_schema(
        description="Получение подробой информации о конкретном продукте",
        summary="Получение подробой информации о конкретном продукте",
        responses={200: ProductDetailSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=RETRIEVE_RESPONSE_EXAMPLE,
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
    ),
    create=extend_schema(
        description="Создать новый продукт в каталоге",
        summary="Создание нового продукта в каталоге",
        request=ProductCatalogSerializer,
        responses={201: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на создание нового продукта в каталоге в Swagger UI",
                summary="Пример запроса на создание нового продукта в каталоге",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=RETRIEVE_RESPONSE_EXAMPLE,
                description="Пример ответа на создание нового продукта в каталоге в Swagger UI",
                summary="Пример ответа на создание нового продукта в каталоге",
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном продукте в каталоге",
        summary="Получить информацию о конкретном продукте в каталоге",
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=UNAUTHORIZED_RESPONSE_EXAMPLE,
                description="Пример ответа для получения информации о конкретном продукте в каталоге в Swagger UI",
                summary="Пример ответа для получения информации о конкретном продукте в каталоге отзыве",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о продукте в каталоге",
        summary="Обновление информации о продукте в каталоге",
        request=ProductCatalogSerializer,
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример запроса на обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value=RETRIEVE_RESPONSE_EXAMPLE,
                description="Пример ответа на обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример ответа на обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о продукте в каталоге",
        summary="Частичное обновление информации о продукте в каталоге",
        request=ProductCatalogSerializer,
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value=PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на частичное обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример запроса на частичное обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value=RETRIEVE_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример ответа на частичное обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить товар из каталога",
        summary="Удалить товар из каталога",
        responses={204: None},
    ),
)
class ProductViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    """
    Возвращает товары с учетом цены в заданном городе.
    """

    queryset = Product.objects.all()
    permission_classes = [ReadOnlyOrAdminPermission]
    characteristics_queryset = Characteristic.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.action in ("list", "frequenly_bought", "popular_products"):
            return ProductCatalogSerializer

        return ProductDetailSerializer
    
    def get_queryset(self):
        self.domain = self.request.query_params.get("city_domain")
        self.queryset = super().get_queryset()

        if self.domain:
            self.queryset = self.queryset.exclude(unavailable_in__domain=self.domain)

        # Annotate cart_quantity for products in the user's cart
        if self.request.user.is_authenticated:
            self.queryset = self.queryset.annotate(
                cart_quantity=Sum(
                    "cart_items__quantity",
                    filter=F("cart_items__customer_id") == self.request.user.id,
                )
            ).order_by("-priority", "title", "-created_at")

        return self.queryset


    @action(detail=True, methods=["get"])
    def frequenly_bought(self, request, *args, **kwargs):

        instance = self.get_object()

        self.queryset = instance.frequenly_bought_together.order_by(
            "product_to__purchase_count"
        )
        return super().list(request, *args, **kwargs)


    @action(methods=["get"], detail=False)
    def popular_products(self, request, *args, **kwargs):
        self.queryset = self.filter_queryset(self.get_queryset()).filter(
            is_popular=True
        )
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        domain = getattr(self, "domain", None)
        filterset = self.filterset_class(self.request.GET, queryset, request=self.request, city_domain=domain)
        qs = filterset.qs
        self.min_qs_price, self.max_qs_price = filterset.min_price, filterset.max_price

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()
            .select_related("category")
            .prefetch_related(
                Prefetch('reviews', queryset=Review.objects.all()),
                Prefetch('additional_categories', queryset=Category.objects.prefetch_related('children')),
                Prefetch('category__children'),
                Prefetch('characteristic_values', queryset=CharacteristicValue.objects.select_related('characteristic')),
                Prefetch('prices', queryset=Price.objects.select_related('city_group').prefetch_related('city_group__cities'))
            )
        )
        brands_queryset = Brand.objects.filter(id__in=queryset.values_list("brand", flat=True))
        brands = BrandSerializer(brands_queryset, many=True).data

        categories_queryset = Category.objects.filter(
            products__in=queryset, is_visible=True
        ).distinct()
        characteristics_queryset = (
            self.characteristics_queryset.filter(
                Q(categories__children__in=categories_queryset)
                | Q(categories__in=categories_queryset),
                for_filtering=True,
            )
            .distinct()
            .prefetch_related(Prefetch("categories", queryset=categories_queryset))
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {
                    "products": serializer.data,
                    "characteristics": CharacteristicFilterSerializer(
                        characteristics_queryset, many=True
                    ).data,
                    "categories": categories_queryset.values("name", "slug"),
                    "brands": brands,
                    "smallest_price": self.min_qs_price,
                    "greatest_price": self.max_qs_price,
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "products": serializer.data,
                "characteristics": CharacteristicFilterSerializer(
                    characteristics_queryset, many=True
                ).data,
            }
        )


    @action(detail=True, methods=["get"])
    def productdetail(self, request, pk=None):
        product = self.get_object()

        serializer = self.get_serializer(product)
        return Response(serializer.data)
