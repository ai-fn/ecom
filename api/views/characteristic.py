from rest_framework.viewsets import ModelViewSet
from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.characteristic import CharacteristicSerializer

from shop.models import Characteristic

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample


CHARACTERISTIC_REQUEST_EXAMPLE = {
                    "name": "Characteristic A",
                    "category": 1,
                    "is_active": True,
                }
CHARACTERISTIC_RESPONSE_EXAMPLE = {
                    "id": 1,
**CHARACTERISTIC_REQUEST_EXAMPLE,
}
CHARACTERISTIC_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(CHARACTERISTIC_REQUEST_EXAMPLE.items())[:2]}



@extend_schema_view(
    list=extend_schema(
        description="Получить список всех характеристик",
        summary="Список характеристик",
        responses={200: CharacteristicSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=CHARACTERISTIC_RESPONSE_EXAMPLE,
                description="Пример ответа для получения списка всех характеристик в Swagger UI",
                summary="Пример ответа для получения списка всех характеристик",
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретной характеристике",
        summary="Информация о характеристике",
        responses={200: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=CHARACTERISTIC_RESPONSE_EXAMPLE,
                description="Пример ответа для получения информации о конкретной характеристике в Swagger UI",
                summary="Пример ответа для получения информации о конкретной характеристике",
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Создать новую характеристику",
        summary="Создание характеристики",
        request=CharacteristicSerializer,
        responses={201: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=CHARACTERISTIC_REQUEST_EXAMPLE,
                description="Пример запроса на создание новой характеристики в Swagger UI",
                summary="Пример запроса на создание новой характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=CHARACTERISTIC_RESPONSE_EXAMPLE,
                description="Пример ответа на создание новой характеристики в Swagger UI",
                summary="Пример ответа на создание новой характеристики",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о характеристике",
        summary="Обновление характеристики",
        request=CharacteristicSerializer,
        responses={200: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=CHARACTERISTIC_REQUEST_EXAMPLE,
                description="Пример запроса на обновление информации о характеристике в Swagger UI",
                summary="Пример запроса на обновление информации о характеристике",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value=CHARACTERISTIC_RESPONSE_EXAMPLE,
                description="Пример ответа на обновление информации о характеристике в Swagger UI",
                summary="Пример ответа на обновление информации о характеристике",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о характеристике",
        summary="Частичное обновление характеристики",
        request=CharacteristicSerializer,
        responses={200: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value=CHARACTERISTIC_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на частичное обновление информации о характеристике в Swagger UI",
                summary="Пример запроса на частичное обновление информации о характеристике",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value=CHARACTERISTIC_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление информации о характеристике в Swagger UI",
                summary="Пример ответа на частичное обновление информации о характеристике",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить характеристику",
        summary="Удаление характеристики",
        responses={204: None},
    ),
)
@extend_schema(tags=["Shop"])
class CharacteristicViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    """Возвращает характеристики продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = Characteristic.objects.all()
    serializer_class = CharacteristicSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
