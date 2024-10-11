from collections import defaultdict

from django.db.models import Sum
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from api.mixins import (
    ActiveQuerysetMixin,
    IntegrityErrorHandlingMixin,
    AnnotateProductMixin,
    DeleteSomeMixin,
)
from cart.models import CartItem
from api.serializers import (
    CartItemSerializer,
    SimplifiedCartItemSerializer,
    ProductDetailSerializer,
)
from shop.models import Product
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
)
from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE, RETRIEVE_RESPONSE_EXAMPLE


CART_ITEM_REQUEST_EXAMPLE = {
    "product_id": 1,
    "quantity": 20,
}
CART_ITEM_RESPONSE_EXAMPLE = {
    "id": 1,
    "product": UNAUTHORIZED_RESPONSE_EXAMPLE,
    "quantity": 20,
}
CART_ITEM_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(CART_ITEM_REQUEST_EXAMPLE.items())[:2]
}


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
        responses={201: CartItemSerializer()},
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
        summary="Удаление нескольких элементов из корзины по id",
        description="Удаление нескольких элементов из корзины по id",
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=CartItemSerializer(),
                examples=[
                    OpenApiExample(
                        "Пример ответа",
                        value={"detail": "'ids' field is required."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Пример запроса", request_only=True, value={"ids": [1, 2, 3]}
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
class CartItemViewSet(
    DeleteSomeMixin,
    AnnotateProductMixin,
    ActiveQuerysetMixin,
    IntegrityErrorHandlingMixin,
    ModelViewSet,
):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.annotate_queryset(
            self.filter_queryset(self.get_queryset()),
            prefix="product__",
            fields=["prices"],
        )
        serializer = self.get_serializer(queryset, many=True).data
        return Response(serializer, status=status.HTTP_200_OK)

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
        queryset = super().get_queryset()

        return queryset.filter(customer=self.request.user)

    @action(methods=["delete"], detail=False)
    def delete_cart(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def get_simple_prods(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Cart items for provided user not found"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def create(self, request, *args, **kwargs):
        existing_cart_items = self.get_queryset()

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

        updated_cart_items = self.get_queryset()
        response_serializer = SimplifiedCartItemSerializer(
            updated_cart_items, many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def cartitems_detail(self, request, *args, **kwargs):
        id_lists = list(self.get_queryset().values_list("product", flat=True))
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
