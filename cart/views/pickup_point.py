from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from cart.models import PickupPoint
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers import PickupPointSerializer, PickupPointDetailSerializer
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiParameter, extend_schema_view, extend_schema


PICKUP_POINT_REQUEST = {
    "coord_x": 48.8566,
    "coord_y": 2.3522,
    "is_active": True,
    "address": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
}
PICKUP_POINT_DETAIL_RESPONSE = {
    "id": 1,
    **PICKUP_POINT_REQUEST,
    "created_at": "2024-10-17T13:49:40.818Z",
    "updated_at": "2024-10-17T13:49:40.818Z",
}
PICKUP_POINT_PARTIAL_UPDAET_REQUEST = {
    k:v for k, v in list(PICKUP_POINT_DETAIL_RESPONSE.items())[:3]
}
PICKUP_POINT_RESPONSE = {
    "id": 1,
    "coordinate": [48.8566, 2.3522],
    "address": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
}

@extend_schema(tags=["cart"])
@extend_schema_view(
    list=extend_schema(
        summary="Получение пунктов выдачи",
        description="Получение пунктов выдачи",
        responses={200: OpenApiResponse(
            response=PickupPointSerializer(many=True),
            examples=[OpenApiExample(
                "Пример ответа",
                response_only=True,
                value=PICKUP_POINT_RESPONSE,
            )],
        )},
        parameters=[OpenApiParameter(
            "city_domain",
            type=str,
            required=True,
            description="Домен города",
        )],
    ),
    retrieve=extend_schema(
        summary="Получение информации о конкретном пункте выдачи",
        description="Получение информации о конкретном пункте выдачи",
        responses={200: OpenApiResponse(
            response=PickupPointSerializer(),
            examples=[OpenApiExample(
                "Пример ответа",
                response_only=True,
                value=PICKUP_POINT_RESPONSE,
            )],
        )},
    ),
    create=extend_schema(
        summary="Добавление информации о пункте выдачи",
        description="Добавление информации о пункте выдачи",
        responses={200: OpenApiResponse(
            response=PickupPointDetailSerializer,
            examples=[OpenApiExample(
                "Пример ответа",
                response_only=True,
                value=PICKUP_POINT_DETAIL_RESPONSE,
            )]
        )},
        examples=[OpenApiExample(
            "Пример запроса",
            request_only=True,
            value=PICKUP_POINT_REQUEST,
        )],
    ),
    update=extend_schema(
        summary="Изменение информации о пункте выдачи",
        description="Изменение информации о пункте выдачи",
        responses={200: OpenApiResponse(
            response=PickupPointDetailSerializer,
            examples=[OpenApiExample(
                "Пример ответа",
                response_only=True,
                value=PICKUP_POINT_DETAIL_RESPONSE,
            )]
        )},
        examples=[OpenApiExample(
            "Пример запроса",
            request_only=True,
            value=PICKUP_POINT_REQUEST,
        )],
    ),
    partial_update=extend_schema(
        summary="Частичное изменение информации о пункте выдачи",
        description="Частичное изменение информации о пункте выдачи",
        responses={200: OpenApiResponse(
            response=PickupPointDetailSerializer,
            examples=[OpenApiExample(
                "Пример ответа",
                response_only=True,
                value=PICKUP_POINT_DETAIL_RESPONSE,
            )]
        )},
        examples=[OpenApiExample(
            "Пример запроса",
            request_only=True,
            value=PICKUP_POINT_PARTIAL_UPDAET_REQUEST,
        )],
    ),
    destroy=extend_schema(
        summary="Удаление информации о пункте выдачи",
        description="Удаление информации о пункте выдачи",
        responses={204: None},
    ),
)
class PickupPointViewSet(ModelViewSet):
    pagination_class = None
    queryset = PickupPoint.objects.all()
    serializer_class = PickupPointSerializer
    permission_classes = [IsAuthenticated, ReadOnlyOrAdminPermission]

    def initial(self, request, *args, **kwargs):
        self.domain = request.query_params.get("city_domain")
        return super().initial(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method.lower() != "get":
            return PickupPointDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        return queryset.filter(is_active=True, city__domain=self.domain)
