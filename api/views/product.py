from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.product_catalog import ProductCatalogSerializer
from api.serializers.product_detail import ProductDetailSerializer
from shop.models import Price, Product
from cart.models import CartItem
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q, Subquery, OuterRef
from rest_framework.response import Response
from rest_framework.decorators import action


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
        ]
    )
    def list(self, request, *args, **kwargs):
        city_domain = request.query_params.get("city_domain")
        price_lte = request.query_params.get("price_lte")
        price_gte = request.query_params.get("price_gte")
        brands = request.query_params.get("brand")
        category = request.query_params.get("category")

        filter_conditions = Q()

        if category:
            filter_conditions &= Q(category__slug=category) | Q(
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
            filtered_queryset.annotate(cart_quantity=Subquery(
                CartItem.objects.filter(customer=self.request.user, product=OuterRef("pk")).count()
            ))

        if not filtered_queryset.exists():
            return Response([])

        self.queryset = filtered_queryset

        return super().list(request, *args, **kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="city_domain",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Домен города для получения цены товара",
            )
        ]
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
