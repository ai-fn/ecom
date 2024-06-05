from django.db.models import Max, Min
from rest_framework.viewsets import ModelViewSet
from api.filters import ProductFilter
from api.mixins import CityPricesMixin
from api.permissions import ReadOnlyOrAdminPermission

from api.serializers.characteristic_filter import CharacteristicFilterSerializer
from api.serializers.product_catalog import ProductCatalogSerializer
from api.serializers.product_detail import ProductDetailSerializer

from shop.models import Category, Price, Product, Characteristic
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.db.models import F, Sum
from rest_framework.response import Response
from rest_framework.decorators import action

from django_filters import rest_framework as filters


@extend_schema(tags=["Shop"])
class ProductViewSet(CityPricesMixin, ModelViewSet):
    """
    Возвращает товары с учетом цены в заданном городе.
    """

    queryset = Product.objects.all().order_by("-created_at")
    permission_classes = [ReadOnlyOrAdminPermission]
    characteristics_queryset = Characteristic.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if (
            self.action == "list"
            or self.action == "frequenly_bought"
            or self.action == "popular_products"
        ):
            return ProductCatalogSerializer
        elif self.action == "productdetail":
            return ProductDetailSerializer

        return ProductDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        self.domain = self.request.query_params.get("city_domain")

        # Annotate cart_quantity for products in the user's cart
        if self.request.user.is_authenticated:
            self.queryset = queryset.annotate(
                cart_quantity=Sum(
                    "cart_items__quantity",
                    filter=F("cart_items__customer_id") == self.request.user.id,
                )
            )

        # Order the queryset by priority
        self.queryset = self.queryset.order_by("priority")

        return self.queryset

    @extend_schema(
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
                value=[
                    {
                        "id": 1,
                        "title": "Product A",
                        "brand": 1,
                        "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                        "slug": "product-a",
                        "city_price": 100.0,
                        "old_price": 120.0,
                        "images": [
                            {
                                "id": 1,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "id": 2,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-a",
                        "in_stock": True,
                        "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                        "in_stock": True,
                    },
                    {
                        "id": 2,
                        "title": "Product B",
                        "brand": 2,
                        "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                        "slug": "product-b",
                        "city_price": 150.0,
                        "old_price": 110.0,
                        "images": [
                            {
                                "id": 1,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "id": 2,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-b",
                        "in_stock": True,
                        "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                        "in_stock": True,
                    },
                ],
            ),
            OpenApiExample(
                name="Authorized Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "title": "Product A",
                        "brand": 1,
                        "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                        "slug": "product-a",
                        "city_price": 100.0,
                        "old_price": 120.0,
                        "images": [
                            {
                                "id": 1,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "id": 2,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-a",
                        "in_stock": True,
                        "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                        "in_stock": True,
                        "cart_quantity": 10,
                    },
                ],
            ),
        ],
    )
    @action(detail=True, methods=["get"])
    def frequenly_bought(self, request, *args, **kwargs):

        instance = self.get_object()

        self.queryset = instance.frequenly_bought_together.order_by(
            "product_to__total_purchase_count"
        )
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получение популярных товаров",
        summary="Получение популярных товаров",
        responses={200: ProductCatalogSerializer(many=True)},
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
    )
    @action(methods=["get"], detail=False)
    def popular_products(self, request, *args, **kwargs):
        self.queryset = self.get_queryset().filter(is_popular=True)
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить список всех продуктов в каталоге",
        summary="Получить список всех продуктов в каталоге",
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Unauthorized Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "title": "Product A",
                        "brand": 1,
                        "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                        "slug": "product-a",
                        "city_price": 100.0,
                        "old_price": 120.0,
                        "images": [
                            {
                                "id": 1,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "id": 2,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-a",
                        "brand_slug": "brand-a",
                        "in_stock": True,
                        "is_popular": True,
                        "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                        "in_stock": True,
                    },
                ],
            ),
            OpenApiExample(
                name="Authorized Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "title": "Product A",
                        "brand": 1,
                        "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                        "slug": "product-a",
                        "city_price": 100.0,
                        "old_price": 120.0,
                        "images": [
                            {
                                "id": 1,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                            {
                                "id": 2,
                                "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                            },
                        ],
                        "category_slug": "category-a",
                        "brand_slug": "brand-a",
                        "in_stock": True,
                        "is_popular": True,
                        "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                        "in_stock": True,
                        "cart_quantity": 10,
                    },
                ],
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
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        characteristics_queryset = Characteristic.objects.filter(characteristicvalue__product__in=queryset, for_filtering=True).distinct()
        categories_queryset = Category.objects.filter(products__in=queryset, is_visible=True).distinct()

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
                    "smallest_price": queryset.aggregate(min_price=Min("prices__price"))["min_price"],
                    "greatest_price": queryset.aggregate(max_price=Max("prices__price"))["max_price"],
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
                        "icon": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        "is_visible": True,
                    },
                    "category_id": 1,
                    "title": "Product A",
                    "brand": {
                        "id": 1,
                        "name": "Deke",
                        "icon": "/media/category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                        "order": 1,
                    },
                    "brand_id": 1,
                    "description": "Product description",
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
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
                            "image_url": "/media/category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/category_icons/7835f40b-88f3-49a3-821c-6ba73126323b.webp",
                        },
                    ],
                    "in_stock": True,
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
        self.domain = request.query_params.get("city_domain")
        if self.domain:
            price_data = (
                Price.objects.filter(
                    product=product, city_group__cities__domain=self.domain
                )
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
                    "title": "Product A",
                    "brand": 1,
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "id": 1,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "in_stock": True,
                    "is_popular": True,
                    "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
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
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "id": 1,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "in_stock": True,
                    "is_popular": True,
                    "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
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
        summary="Получить информацию о конкретном продукте в каталоге",
        responses={200: ProductCatalogSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "title": "Product A",
                    "brand": 1,
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "id": 1,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "is_popular": True,
                    "in_stock": True,
                },
                description="Пример ответа для получения информации о конкретном продукте в каталоге в Swagger UI",
                summary="Пример ответа для получения информации о конкретном продукте в каталоге отзыве",
                media_type="application/json",
            ),
        ],
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
                    "title": "Updated Product A",
                    "brand": 1,
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "id": 1,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "in_stock": True,
                    "is_popular": True,
                    "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
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
                    "title": "Product A",
                    "brand": 1,
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "id": 1,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "in_stock": True,
                    "is_popular": True,
                    "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                    "in_stock": True,
                },
                description="Пример ответа на обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример ответа на обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
        ],
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
                    "brand": 1,
                    "image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "ivborw0kggoaaaansuheugaaaaoaaaakcayaaacnms+9aaaa3eleqvr4nk2psureqbrf79udl0limbacvtnkdlmtbitugk2+ild/kejima/wo2ysbstrsvlb0moiqnzmooz5duiwso2nvlzoaf4bagarobzt10qkwuvhoiie67p+i6lpnseane1zkyjnxhiiydsrvsqlnmeypnjvb6jrukul1crlsnnmpndowtkhay2stzi+jmzn9konw3dtvt/p+/6jmrdrfgvxhcpp8x+/crzv6zfvrkqqwzrnj7twyyaijpl5suq6szklvbvlwyy7mx8hd4imj/npbo/lc6cizdfxzep/cizmgqaaaabjru5erkjggg==",
                    "slug": "product-a",
                    "city_price": 100.0,
                    "old_price": 120.0,
                    "images": [
                        {
                            "id": 1,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                        {
                            "id": 2,
                            "image_url": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                        },
                    ],
                    "category_slug": "category-a",
                    "brand_slug": "brand-a",
                    "in_stock": True,
                    "is_popular": True,
                    "search_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "catalog_image": "/media/catalog/products/image-b04109e4-a711-498e-b267-d0f9ebcac550.webp",
                    "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma/wO2ysBStrsVlB0MoiQnZmooZ5duIWso2nvlzOAf4bAgARobZt10QkWuvHoiie67p+I6LPnSEANE1zKyJnxhiIyDsRvSqlNmEYPnjvb6jrukul1CrLsnNmPnDOwTkHay2stZi+JmzN9koNw3DtvT/p+/6JmRdRFGVxHCPP8x+/cRzv6ZfvrKqqwzRNj7TWyyAIjpl5SUQ6SZKLvbVlWYY7MX8hd4imj/npbO/lC6CIzDfxzEp/CIzmgQAAAABJRU5ErkJggg==",
                    "in_stock": True,
                    "cart_quantity": 10,
                },
                description="Пример ответа на частичное обновление информации о продукте в каталоге в Swagger UI",
                summary="Пример ответа на частичное обновление информации о продукте в каталоге",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить товар из каталога",
        summary="Удалить товар из каталога",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
