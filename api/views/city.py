from rest_framework import viewsets

from account.models import City
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city import CitySerializer

from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    tags=['City']
)
class CityViewSet(viewsets.ModelViewSet):
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
                value=[{
                    "id": 1,
                    "name": "Воронеж",
                    "domain": "example.com",
                    "nominative_case": "Воронеж",
                    "genitive_case": "Воронежа",
                    "dative_case": "Воронежу",
                    "accusative_case": "Воронежем",
                    "instrumental_case": "Воронежем",
                    "prepositional_case": "Воронеже",
                }],
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
        responses={204: "No Content"},
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
