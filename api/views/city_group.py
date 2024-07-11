from rest_framework.viewsets import ModelViewSet

from account.models import CityGroup
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city_group import CityGroupSerializer

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(tags=["City"])
class CityGroupViewSet(ModelViewSet):
    """Возвращает группы городов

    Args:
        viewsets (_type_): _description_
    """

    queryset = CityGroup.objects.all().order_by("-created_at")
    serializer_class = CityGroupSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех групп городов.",
        summary="Список групп городов",
        examples=[
            OpenApiExample(
                name="List City Groups Example",
                value={
                    "id": 1,
                    "name": "Group A",
                    "is_active": True,
                    "main_city": {
                        "id": 1,
                        "name": "Воронеж",
                        "domain": "example.com",
                        "nominative_case": "Воронеж",
                        "genitive_case": "Воронежа",
                        "dative_case": "Воронежу",
                        "accusative_case": "Воронежем",
                        "instrumental_case": "Воронежем",
                        "prepositional_case": "Воронеже",
                        "is_active": True,
                    },
                    "cities": [
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
                            "is_active": True,
                        },
                    ],
                },
                description="Пример ответа при запросе списка групп городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретной группе городов.",
        summary="Информация о группе городов",
        examples=[
            OpenApiExample(
                name="Retrieve City Group Example",
                value={
                    "id": 1,
                    "name": "Group A",
                    "is_active": True,
                    "main_city": {
                        "id": 1,
                        "name": "City A",
                        "domain": "example.com",
                        "nominative_case": "City A",
                        "genitive_case": "City A",
                        "dative_case": "City A",
                        "accusative_case": "City A",
                        "instrumental_case": "City A",
                        "prepositional_case": "City A",
                        "is_active": True,
                    },
                    "cities": [
                        {
                            "id": 1,
                            "name": "City A",
                            "domain": "example.com",
                            "nominative_case": "City A",
                            "genitive_case": "City A",
                            "dative_case": "City A",
                            "accusative_case": "City A",
                            "instrumental_case": "City A",
                            "prepositional_case": "City A",
                            "is_active": True,
                        },
                    ],
                },
                description="Пример ответа при запросе информации о группе городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создать новую группу городов.",
        summary="Создание группы городов",
        request=CityGroupSerializer,
        responses={201: CityGroupSerializer},
        examples=[
            OpenApiExample(
                name="Create City Group Example",
                request_only=True,
                value={
                    "name": "New Group",
                    "main_city": 1,
                    "cities": [1],
                },
                description="Пример запроса для создания новой группы городов в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="List City Groups Example",
                value={
                    "id": 1,
                    "name": "Group A",
                    "is_active": True,
                    "main_city": {
                        "id": 1,
                        "name": "City A",
                        "domain": "example.com",
                        "nominative_case": "City A",
                        "genitive_case": "City A",
                        "dative_case": "City A",
                        "accusative_case": "City A",
                        "instrumental_case": "City A",
                        "prepositional_case": "City A",
                        "is_active": True,
                    },
                    "cities": [
                        {
                            "id": 1,
                            "name": "City A",
                            "domain": "example.com",
                            "nominative_case": "City A",
                            "genitive_case": "City A",
                            "dative_case": "City A",
                            "accusative_case": "City A",
                            "instrumental_case": "City A",
                            "prepositional_case": "City A",
                            "is_active": True,
                        },
                    ],
                },
                description="Пример ответа для создания новой группы городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о группе городов.",
        summary="Обновление информации о группе городов",
        request=CityGroupSerializer,
        responses={200: CityGroupSerializer},
        examples=[
            OpenApiExample(
                name="Update City Group Example",
                request_only=True,
                value={
                    "name": "Updated Group",
                    "main_city": 1,
                    "cities": [
                        1,
                    ],
                },
                description="Пример запроса для обновления информации о группе городов в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="List City Groups Example",
                value={
                    "id": 1,
                    "name": "Updated Group",
                    "main_city": {
                        "id": 1,
                        "name": "Воронеж",
                        "domain": "example.com",
                        "nominative_case": "Воронеж",
                        "genitive_case": "Воронежа",
                        "dative_case": "Воронежу",
                        "accusative_case": "Воронежем",
                        "instrumental_case": "Воронежем",
                        "prepositional_case": "Воронеже",
                        "is_active": True,
                    },
                    "cities": [
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
                            "is_active": True,
                        },
                    ],
                },
                description="Пример ответа для обновления информации о группе городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о группе городов.",
        summary="Частичное обновление информации о группе городов",
        request=CityGroupSerializer,
        responses={200: CityGroupSerializer},
        examples=[
            OpenApiExample(
                name="Partial Update City Group Example",
                request_only=True,
                value={
                    "name": "Updated Group",
                },
                description="Пример запроса для частичного обновления информации о группе городов в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update City Group Example",
                response_only=True,
                value={
                    "id": 1,
                    "name": "Updated Group",
                    "main_city": {
                        "id": 1,
                        "name": "Воронеж",
                        "domain": "example.com",
                        "nominative_case": "Воронеж",
                        "genitive_case": "Воронежа",
                        "dative_case": "Воронежу",
                        "accusative_case": "Воронежем",
                        "instrumental_case": "Воронежем",
                        "prepositional_case": "Воронеже",
                        "is_active": True,
                    },
                    "cities": [
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
                            "is_active": True,
                        },
                    ],
                },
                description="Пример запроса для частичного обновления информации о группе городов в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить группу городов.",
        summary="Удаление группы городов",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Delete City Group Example",
                response_only=True,
                value=None,
                description="Пример ответа для удаления группы городов в Swagger UI",
                media_type="application/json",
            ),
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
