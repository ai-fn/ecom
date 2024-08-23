from rest_framework.viewsets import ModelViewSet
from api.filters import PriceFilter
from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.price import PriceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from shop.models import Price

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample

PRICE_REQUEST_EXAMPLE = {
    "product": 1,
    "city_group": 1,
    "price": 100.0,
    "is_active": True,
}
PRICE_RESPONSE_EXAMPLE = {
    "id": 1,
    "product": 1,
    "city_group": 1,
    "price": 100.0,
    "is_active": True,
}
PRICE_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(PRICE_REQUEST_EXAMPLE.items())[:3]}

@extend_schema_view(
    list=extend_schema(
        description="Получить список всех цен на продукты",
        summary="Список цен на продукты",
        responses={200: PriceSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=PRICE_RESPONSE_EXAMPLE,
                description="Пример ответа для получения списка всех цен на продукты в Swagger UI",
                summary="Пример ответа для получения списка всех цен на продукты",
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретной цене на продукт",
        summary="Информация о цене на продукт",
        responses={200: PriceSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=PRICE_RESPONSE_EXAMPLE,
                description="Пример ответа для получения информации о конкретной цене на продукт в Swagger UI",
                summary="Пример ответа для получения информации о конкретной цене на продукт",
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Создать новую цену на продукт",
        summary="Создание цены на продукт",
        request=PriceSerializer,
        responses={201: PriceSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=PRICE_REQUEST_EXAMPLE,
                description="Пример запроса на создание новой цены на продукт в Swagger UI",
                summary="Пример запроса на создание новой цены на продукт",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=PRICE_RESPONSE_EXAMPLE,
                description="Пример ответа на создание новой цены на продукт в Swagger UI",
                summary="Пример ответа на создание новой цены на продукт",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о цене на продукт",
        summary="Обновление цены на продукт",
        request=PriceSerializer,
        responses={200: PriceSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=PRICE_REQUEST_EXAMPLE,
                description="Пример запроса на обновление информации о цене на продукт в Swagger UI",
                summary="Пример запроса на обновление информации о цене на продукт",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value=PRICE_RESPONSE_EXAMPLE,
                description="Пример ответа на обновление информации о цене на продукт в Swagger UI",
                summary="Пример ответа на обновление информации о цене на продукт",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о цене на продукт",
        summary="Частичное обновление цены на продукт",
        request=PriceSerializer,
        responses={200: PriceSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value=PRICE_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на частичное обновление информации о цене на продукт в Swagger UI",
                summary="Пример запроса на частичное обновление информации о цене на продукт",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value=PRICE_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление информации о цене на продукт в Swagger UI",
                summary="Пример ответа на частичное обновление информации о цене на продукт",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить цену на продукт",
        summary="Удаление цены на продукт",
        responses={204: None},
    ),
)
@extend_schema(tags=["Shop"])
class PriceViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    queryset = Price.objects.order_by("-created_at")
    serializer_class = PriceSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PriceFilter
