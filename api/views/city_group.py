from rest_framework.viewsets import ModelViewSet

from account.models import CityGroup
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.city_group import CityGroupSerializer

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample
from api.views.city import CITY_RESPONSE_EXAMPLE


CITY_GROUP_REQUEST_EXAMPLE = {
    "name": "Group A",
    "is_active": True,
    "main_city": 1,
    "cities": [1, 2, 3],
}
CITY_GROUP_RESPONSE_EXAMPLE = {
    "id": 1,
    "main_city": CITY_RESPONSE_EXAMPLE,
    "cities": [CITY_RESPONSE_EXAMPLE],
    **CITY_GROUP_REQUEST_EXAMPLE,
}
CITY_GROUP_PARTIAL_UPDATE_REQEUST_EXAMPLE = {k: v for k, v in list(CITY_GROUP_REQUEST_EXAMPLE.items())[:2]}

@extend_schema_view(
    list=extend_schema(
        description="Получить список всех групп городов.",
        summary="Список групп городов",
        examples=[
            OpenApiExample(
                name="List City Groups Example",
                value=CITY_GROUP_RESPONSE_EXAMPLE,
                description="Пример ответа при запросе списка групп городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретной группе городов.",
        summary="Информация о группе городов",
        examples=[
            OpenApiExample(
                name="Retrieve City Group Example",
                value=CITY_GROUP_RESPONSE_EXAMPLE,
                description="Пример ответа при запросе информации о группе городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Создать новую группу городов.",
        summary="Создание группы городов",
        request=CityGroupSerializer,
        responses={201: CityGroupSerializer},
        examples=[
            OpenApiExample(
                name="Create City Group Example",
                request_only=True,
                value=CITY_GROUP_REQUEST_EXAMPLE,
                description="Пример запроса для создания новой группы городов в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="List City Groups Example",
                value=CITY_GROUP_RESPONSE_EXAMPLE,
                description="Пример ответа для создания новой группы городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о группе городов.",
        summary="Обновление информации о группе городов",
        request=CityGroupSerializer,
        responses={200: CityGroupSerializer},
        examples=[
            OpenApiExample(
                name="Update City Group Example",
                request_only=True,
                value=CITY_GROUP_REQUEST_EXAMPLE,
                description="Пример запроса для обновления информации о группе городов в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update City Groups Example",
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример ответа для обновления информации о группе городов в Swagger UI",
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о группе городов.",
        summary="Частичное обновление информации о группе городов",
        request=CityGroupSerializer,
        responses={200: CityGroupSerializer},
        examples=[
            OpenApiExample(
                name="Partial Update City Group Example",
                request_only=True,
                value=CITY_GROUP_PARTIAL_UPDATE_REQEUST_EXAMPLE,
                description="Пример запроса для частичного обновления информации о группе городов в Swagger UI",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update City Group Example",
                response_only=True,
                value=CITY_RESPONSE_EXAMPLE,
                description="Пример запроса для частичного обновления информации о группе городов в Swagger UI",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
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
    ),
)
@extend_schema(tags=["City"])
class CityGroupViewSet(ModelViewSet):
    """Возвращает группы городов

    Args:
        viewsets (_type_): _description_
    """

    queryset = CityGroup.objects.order_by("-created_at")
    serializer_class = CityGroupSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
