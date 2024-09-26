from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, AnnotateProductMixin
from shop.models import FavoriteProduct
from api.serializers import FavoriteProductSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter, OpenApiResponse
from rest_framework.permissions import IsAuthenticated

from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE


FAVORITE_PRODUCT_CREATE_REQUEST_EXAMPLE = {
    "products_ids": [1, 2, 3],
}

FAVORITE_PRODUCT_CREATE_REQUEST_EXAMPLE_WITH_USER_ID = {
    "user_id": 1,
    **FAVORITE_PRODUCT_CREATE_REQUEST_EXAMPLE,
}
FAVORITE_PRODUCT_REQUEST_EXAMPLE = {
    "user_id": 2,
    "product_id": 1,
}
FAVORITE_PRODUCT_RESPONSE_EXAMPLE = {
    "id": 1,
    "user_id": 2,
    "product":  UNAUTHORIZED_RESPONSE_EXAMPLE,
}

@extend_schema_view(
    list=extend_schema(
        summary="Список избранных продуктов",
        description="Возвращает список всех избранных продуктов.",
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример списка избранных продуктов",
                description="Пример ответа, содержащего список избранных продуктов.",
                value=FAVORITE_PRODUCT_RESPONSE_EXAMPLE,
            )
        ],
    ),
    create=extend_schema(
        summary="Добавить избранный продукт",
        description="Добавляет новый избранный продукт.",
        examples=[
            OpenApiExample(
                "Пример запроса (с указанием user_id)",
                summary="Пример запроса на добавление избранного продукта (с указанием user_id)",
                description="Пример тела запроса для добавления нового избранного продукта.",
                value=FAVORITE_PRODUCT_CREATE_REQUEST_EXAMPLE_WITH_USER_ID,
                request_only=True,
            ),
            OpenApiExample(
                "Пример запроса (без указания user_id)",
                summary="Пример запроса на добавление избранного продукта (без указания user_id)",
                description="Пример тела запроса для добавления нового избранного продукта.",
                value=FAVORITE_PRODUCT_CREATE_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при добавлении избранного продукта",
                description="Пример успешного ответа, содержащего добавленный избранный продукт.",
                response_only=True,
                value=[FAVORITE_PRODUCT_RESPONSE_EXAMPLE]
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Получить избранный продукт",
        description="Возвращает избранный продукт по ID.",
        examples=[
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример ответа для одного избранного продукта",
                description="Пример ответа, содержащего данные одного избранного продукта.",
                value=FAVORITE_PRODUCT_RESPONSE_EXAMPLE
            )
        ],
    ),
    update=extend_schema(
        summary="Обновить избранный продукт",
        description="Обновляет информацию об избранном продукте.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на обновление избранного продукта",
                description="Пример тела запроса для обновления существующего избранного продукта.",
                value=FAVORITE_PRODUCT_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при обновлении избранного продукта",
                description="Пример успешного ответа, содержащего обновленный избранный продукт.",
                value=FAVORITE_PRODUCT_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Частично обновить избранный продукт",
        description="Частично обновляет информацию об избранном продукте.",
        examples=[
            OpenApiExample(
                "Пример запроса",
                summary="Пример запроса на частичное обновление избранного продукта",
                description="Пример тела запроса для частичного обновления существующего избранного продукта.",
                value={"product_id": 5118},
                request_only=True,
            ),
            OpenApiExample(
                "Пример успешного ответа",
                summary="Пример успешного ответа при частичном обновлении избранного продукта",
                description="Пример успешного ответа, содержащего частично обновленный избранный продукт.",
                value=FAVORITE_PRODUCT_RESPONSE_EXAMPLE,
                response_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Удалить избранный продукт",
        description="Удаляет избранный продукт.",
    ),
    delete_by_prod=extend_schema(
        operation_id='delete_favorite_by_product_id',
        summary='Удаление продукта из избранного по ID продукта',
        description='Удаление продукта из избранного по ID продукта.',
        parameters=[
            OpenApiParameter(
                name='product_id',
                location=OpenApiParameter.PATH,
                description='ID продукта для удаления из избранного',
                required=True,
                type=int
            )
        ],
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(description='Продукт успешно удален из избранного'),
            HTTP_404_NOT_FOUND: OpenApiResponse(description='Продукт не найден в избранном')
        },
        methods=['DELETE'],
    ),
)
@extend_schema(
    tags=["Shop"],
    parameters=[
        OpenApiParameter(
            name="city_domain",
            description="Домен города, для получения цен",
            required=False,
        ),
    ]
)
class FavoriteProductViewSet(AnnotateProductMixin, ActiveQuerysetMixin, IntegrityErrorHandlingMixin, CacheResponse, viewsets.ModelViewSet):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["city_domain"] = self.request.query_params.get("city_domain")
        return context

    def get_queryset(self):
        return self.annotate_queryset(super().get_queryset().filter(user=self.request.user), prefix="product__")

    def create(self, request, *args, **kwargs):
        products_ids: list[int] = request.data.get("products_ids")
        if not products_ids:
            return Response({"detail": "products_ids is required"}, status=HTTP_400_BAD_REQUEST)

        if not (user_id := request.data.get("user_id")):
            user_id = self.request.user.pk
        
        existing_fav_prods = set(self.filter_queryset(self.get_queryset()).values_list("product__id", flat=True))
        difference = set(products_ids).difference(existing_fav_prods)

        for product_id in difference:
            serializer = self.get_serializer(data={"product_id": product_id, "user_id": user_id})
            serializer.is_valid(raise_exception=True)
            serializer.save()

        queryset = self.filter_queryset(self.get_queryset())
        return Response(self.get_serializer(queryset, many=True).data, status=HTTP_200_OK)


    @action(detail=False, methods=['delete'], url_path='delete-by-product-id/(?P<product_id>\d+)')
    def delete_by_prod(self, request, product_id=None, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            queryset.get(product__id=product_id).delete()
        except FavoriteProduct.DoesNotExist:
            return Response({"detail": f"Favorite product with product_id '{product_id}' not found."}, status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)
