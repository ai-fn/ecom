from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import PromoSerializer
from shop.models import Promo
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from api.views.city import CITY_RESPONSE_EXAMPLE
from api.views.category import CATEGORY_DETAIL_RESPONSE_EXAMPLE
from api.views.product import UNAUTHORIZED_RESPONSE_EXAMPLE


PROMO_REQUEST_EXAMPLE = {
    "name": "Test",
    "is_active": True,
    "products_id": [1, 2, 3],
    "cities_id": [1, 2, 3],
    "categories_id": [1, 2, 3],
    "active_to": "2024-04-05",
    "image": "/media/promo/image-70e50210-8678-4b3a-90f9-3626526c11cb.webp",
    "thumb_img": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAA3ElEQVR4nK2PsUrEQBRF79udl0lIMBACVtnKdlmtbITUgk2+ILD/kEJIma",
}
PROMO_RESPONSE_EXAMPLE = {
    "id": 1,
    **PROMO_REQUEST_EXAMPLE,
    "categories": [CATEGORY_DETAIL_RESPONSE_EXAMPLE],
    "products": [UNAUTHORIZED_RESPONSE_EXAMPLE],
    "cities": [CITY_RESPONSE_EXAMPLE],
}
PROMO_RESPONSE_EXAMPLE.pop("products_id")
PROMO_RESPONSE_EXAMPLE.pop("categories_id")
PROMO_RESPONSE_EXAMPLE.pop("cities_id")

PROMO_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(PROMO_REQUEST_EXAMPLE.items())[:2]}


@extend_schema_view(
    list=extend_schema(
        description="Получение списка промо акций",
        summary="Получение списка промо акций",
        operation_id="api_promos_list",
        responses={200: PromoSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на получение списка всех промо акций",
                response_only=True,
                value=PROMO_RESPONSE_EXAMPLE,
            )
        ],
    ),
    retrieve=extend_schema(
        description="Получение промо акции по уникальному идентификатору",
        summary="Получение промо акции по уникальному идентификатору",
        operation_id="api_promos_retrieve",
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на получение промо акции",
                response_only=True,
                value=PROMO_RESPONSE_EXAMPLE,
            )
        ],
    ),
    create=extend_schema(
        description="Создание промо акции",
        summary="Создание промо акции",
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на создание промо акции",
                response_only=True,
                value=PROMO_RESPONSE_EXAMPLE,
            ),
            OpenApiExample(
                name="Request Example",
                description="Пример запроса на создание промо акции",
                response_only=True,
                value=PROMO_REQUEST_EXAMPLE,
            ),
        ],
    ),
    update=extend_schema(
        description="Обновление промо акции",
        summary="Обновление промо акции",
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на обновление промо акции",
                response_only=True,
                value=PROMO_RESPONSE_EXAMPLE,
            ),
            OpenApiExample(
                name="Request Example",
                description="Пример запроса на обновление промо акции",
                response_only=True,
                value=PROMO_REQUEST_EXAMPLE,
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частичное обновление промо акции",
        summary="Частичное обновление промо акции",
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на частичное обновление промо акции",
                response_only=True,
                value=PROMO_RESPONSE_EXAMPLE,
            ),
            OpenApiExample(
                name="Request Example",
                description="Пример запроса на частичное обновление промо акции",
                response_only=True,
                value=PROMO_PARTIAL_UPDATE_REQUEST_EXAMPLE,
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удаление промо акции",
        summary="Удаление промо акции",
        responses={204: None},
    ),
    active_promos=extend_schema(
        summary="Получение списка активных промо акций",
        description="Получение списка активных промо акций",
        responses={200: PromoSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Response Example",
                description="Пример ответа на получение списка активных промо акций",
                response_only=True,
                value=PROMO_RESPONSE_EXAMPLE,
            ),
        ],
    ),
)
@extend_schema(
    tags=["Shop"],
    parameters=[
        OpenApiParameter(
            name="domain",
            description="Домен города",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        )
    ],
)
class PromoViewSet(ModelViewSet):

    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    def get_permissions(self):
        if self.action == "active_promos":
            return [AllowAny()]

        return super().get_permissions()

    def get_queryset(self):
        self.domain = self.request.query_params.get("domain")
        return self.queryset.filter(cities__domain=self.domain).distinct()

    @action(methods=["get"], detail=False)
    def active_promos(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(is_active=True)
        return super().list(request, *args, **kwargs)
