from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from account.models import City
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city import CitySerializer

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample, OpenApiParameter
from django.db.models import Case, When, Value, IntegerField

SIMPLIFIED_CITY_GROUP_RESPONSE_EXAMPLE = {
    "id": 1,
    "name": None,
    "is_active": True,
}

CITY_REQUEST_EXAMPLE = {
    "name": "Воронеж",
    "domain": "example.com",
    "nominative_case": "Воронеж",
    "genitive_case": "Воронежа",
    "dative_case": "Воронежу",
    "accusative_case": "Воронежем",
    "instrumental_case": "Воронежем",
    "prepositional_case": "Воронеже",
    "is_active": True,
    "city_group": 1,
}
CITY_RESPONSE_EXAMPLE = {
    "id": 1,
    "city_group": SIMPLIFIED_CITY_GROUP_RESPONSE_EXAMPLE,
    ** CITY_REQUEST_EXAMPLE,
}
CITY_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(CITY_REQUEST_EXAMPLE.items())[:2]
}

@extend_schema_view(
    list=extend_schema(
        description="Получить список всех городов.",
        summary="Список городов",
        examples=[
            OpenApiExample(
                name="List Cities Example",
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример ответа при запросе списка городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном городе.",
        summary="Информация о городе",
        examples=[
            OpenApiExample(
                name="Retrieve City Example",
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример ответа при запросе информации о городе в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Создать новый город.",
        summary="Создание города",
        request=CitySerializer,  
        responses={201: CitySerializer()},
        examples=[
            OpenApiExample(
                name="Create City Example",
                request_only=True,
                value=CITY_REQUEST_EXAMPLE,
                description="Пример запроса для создания нового города в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create City Example",
                response_only=True,
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример ответа для создания нового города в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о городе.",
        summary="Обновление информации о городе",
        request=CitySerializer,
        responses={200: CitySerializer()},
        examples=[
            OpenApiExample(
                name="Update City Example",
                request_only=True,
                value=CITY_REQUEST_EXAMPLE,
                description="Пример запроса для обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update City Example",
                request_only=True,
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример ответа для обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о городе.",
        summary="Частичное обновление информации о городе",
        request=CitySerializer,
        responses={200: CitySerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update City Example",
                request_only=True,
                value=CITY_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса для частичного обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update City Example",
                response_only=True,
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример ответа для частичного обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить город.",
        summary="Удаление города",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Delete City Example",
                response_only=True,
                value=None,
                description="Пример ответа для удаления города в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    search=extend_schema(
        description="Поиск города по названию",
        summary="Поиск города по названию",
        request=CitySerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="city_name",
                default="Но",
                description="Название города для поиска",
            )
        ],
        examples=[
            OpenApiExample(
                name="Response Example",
                response_only=True,
                value=CITY_RESPONSE_EXAMPLE,
            )
        ],
    ),
    all_cities=extend_schema(
        description="Получение списка всех городов",
        summary="Получение списка всех городов",
        responses={200: CitySerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Get All Cities Example",
                response_only=True,
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример запроса для получения всех городов в Swagger UI",
                media_type="application/json",
            ),
        ]
    ),
)
@extend_schema(tags=["City"])
class CityViewSet(ModelViewSet):
    """Возвращает города
    Args:
        viewsets (_type_): _description_
    """

    queryset = City.objects.all().order_by("-population")
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAdminPermission]


    @action(detail=False, methods=["get"])
    def all_cities(self, request, *args, **kwargs):
        return Response(
            {"results": CitySerializer(self.queryset, many=True).data},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        city_name = request.query_params.get("city_name")
        if not city_name:
            return response.Response(
                {"error": "City name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        relevance_criteria = Case(
            When(name__iexact=city_name, then=Value(3)),
            When(name__istartswith=city_name, then=Value(2)),
            When(name__icontains=city_name, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )

        queryset = (
            self.queryset.filter(name__icontains=city_name)
            .annotate(relevance=relevance_criteria)
            .order_by("-relevance")
        )
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
