from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from account.models import City
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city import CitySerializer

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from django.db.models import Case, When, Value, IntegerField


@extend_schema(tags=["City"])
class CityViewSet(ModelViewSet):
    """Возвращает города
    Args:
        viewsets (_type_): _description_
    """

    queryset = City.objects.all().order_by("-created_at")
    serializer_class = CitySerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех городов.",
        summary="Список городов",
        examples=[
            OpenApiExample(
                name="List Cities Example",
                value=[
                    {
                        "id": 1,
                        "name": "Воронеж",
                        "domain": "example.com",
                        "nominative_case": "Воронеж",
                        "genitive_case": "Воронежа",
                        "dative_case": "Воронежу",
                        "accusative_case": "Воронежем",
                        "instrumental_case": "Воронежем",
                        "prepositional_case": "Воронеже",
                    }
                ],
                description="Пример ответа при запросе списка городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном городе.",
        summary="Информация о городе",
        examples=[
            OpenApiExample(
                name="Retrieve City Example",
                value={
                    "id": 1,
                    "name": "Воронеж",
                    "domain": "example.com",
                    "nominative_case": "Воронеж",
                    "genitive_case": "Воронежа",
                    "dative_case": "Воронежу",
                    "accusative_case": "Воронежем",
                    "instrumental_case": "Воронежем",
                    "prepositional_case": "Воронеже",
                },
                description="Пример ответа при запросе информации о городе в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создать новый город.",
        summary="Создание города",
        request=CitySerializer,  # Пример запроса будет взят из сериализатора
        responses={201: CitySerializer()},  # Пример ответа будет взят из сериализатора
        examples=[
            OpenApiExample(
                name="Create City Example",
                request_only=True,
                value={
                    "name": "Воронеж",
                    "domain": "example.com",
                    "nominative_case": "Воронеж",
                    "genitive_case": "Воронежа",
                    "dative_case": "Воронежу",
                    "accusative_case": "Воронежем",
                    "instrumental_case": "Воронежем",
                    "prepositional_case": "Воронеже",
                },
                description="Пример запроса для создания нового города в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create City Example",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Воронеж",
                    "domain": "example.com",
                    "nominative_case": "Воронеж",
                    "genitive_case": "Воронежа",
                    "dative_case": "Воронежу",
                    "accusative_case": "Воронежем",
                    "instrumental_case": "Воронежем",
                    "prepositional_case": "Воронеже",
                },
                description="Пример ответа для создания нового города в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о городе.",
        summary="Обновление информации о городе",
        request=CitySerializer,
        responses={200: CitySerializer()},
        examples=[
            OpenApiExample(
                name="Update City Example",
                request_only=True,
                value={
                    "name": "Москва",
                    "domain": "example.com",
                    "nominative_case": "Москва",
                    "genitive_case": "Москвы",
                    "dative_case": "Москве",
                    "accusative_case": "Москвой",
                    "instrumental_case": "Москвой",
                    "prepositional_case": "Москве",
                },
                description="Пример запроса для обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update City Example",
                request_only=True,
                value={
                    "id": 1,
                    "name": "Москва",
                    "domain": "example.com",
                    "nominative_case": "Москва",
                    "genitive_case": "Москвы",
                    "dative_case": "Москве",
                    "accusative_case": "Москвой",
                    "instrumental_case": "Москвой",
                    "prepositional_case": "Москве",
                },
                description="Пример ответа для обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о городе.",
        summary="Частичное обновление информации о городе",
        request=CitySerializer,
        responses={200: CitySerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update City Example",
                request_only=True,
                value={
                    "domain": "updatedcity.com",
                },
                description="Пример запроса для частичного обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update City Example",
                request_only=True,
                value={
                    "name": "Москва",
                    "domain": "updatedcity.com",
                    "nominative_case": "Москва",
                    "genitive_case": "Москвы",
                    "dative_case": "Москве",
                    "accusative_case": "Москвой",
                    "instrumental_case": "Москвой",
                    "prepositional_case": "Москве",
                },
                description="Пример запроса для частичного обновления информации о городе в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
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
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="Поиск города по названию",
        summary="Поиск города по названию",
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
                value=[
                    {
                        "id": 11,
                        "name": "Новосибирск",
                        "domain": "Новосибирск.ru",
                        "nominative_case": "Новосибирск",
                        "genitive_case": "Новосибирска",
                        "dative_case": "Новосибирску",
                        "accusative_case": "Новосибирск",
                        "instrumental_case": "Новосибирском",
                        "prepositional_case": "Новосибирске",
                    },
                    {
                        "id": 13,
                        "name": "Нижний Новгород",
                        "domain": "НижнийНовгород.ru",
                        "nominative_case": "Нижний Новгород",
                        "genitive_case": "Нижний Новгорода",
                        "dative_case": "Нижний Новгороду",
                        "accusative_case": "Нижний Новгород",
                        "instrumental_case": "Нижний Новгородом",
                        "prepositional_case": "Нижний Новгороде",
                    },
                ],
            )
        ],
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
