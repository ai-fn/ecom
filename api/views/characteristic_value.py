from rest_framework.viewsets import ModelViewSet
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.characteristic_value import CharacteristicValueSerializer

from shop.models import CharacteristicValue
from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=['Shop']
)
class CharacteristicValueViewSet(ModelViewSet):
    """Возвращает значение характеристик продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = CharacteristicValue.objects.all().order_by("-created_at")
    serializer_class = CharacteristicValueSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех значений характеристик",
        summary="Список значений характеристик",
        responses={200: CharacteristicValueSerializer(many=True)},
        examples=[
            OpenApiExample(
                name='List Response Example',
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "characteristic_name": "Characteristic A",
                        "value": "Value A"
                    },
                    {
                        "id": 2,
                        "characteristic_name": "Characteristic B",
                        "value": "Value B"
                    },
                    # Добавьте другие значения характеристик, если есть
                ],
                description="Пример ответа для получения списка всех значений характеристик в Swagger UI",
                summary="Пример ответа для получения списка всех значений характеристик",
                media_type="application/json",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретном значении характеристики",
        summary="Информация о значении характеристики",
        responses={200: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name='Retrieve Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "characteristic_name": "Characteristic A",
                    "value": "Value A"
                },
                description="Пример ответа для получения информации о конкретном значении характеристики в Swagger UI",
                summary="Пример ответа для получения информации о конкретном значении характеристики",
                media_type="application/json",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создать новое значение характеристики",
        summary="Создание значения характеристики",
        request=CharacteristicValueSerializer,
        responses={201: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name='Create Request Example',
                request_only=True,
                value={
                    "characteristic_id": 1,
                    "product_id": 6,
                    "value": "New Value A"
                },
                description="Пример запроса на создание нового значения характеристики в Swagger UI",
                summary="Пример запроса на создание нового значения характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Create Response Example',
                response_only=True,
                value={
                    "id": 222,
                    "characteristic_name": "Выбранный цвет",
                    "value": "New Value A"
                },
                description="Пример ответа на создание нового значения характеристики в Swagger UI",
                summary="Пример ответа на создание нового значения характеристики",
                media_type="application/json",
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о значении характеристики",
        summary="Обновление значения характеристики",
        request=CharacteristicValueSerializer,
        responses={200: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name='Update Request Example',
                request_only=True,
                value={
                    "characteristic_id": 1,
                    "product_id": 13,
                    "value": "Updated Value B"
                },
                description="Пример запроса на обновление информации о значении характеристики в Swagger UI",
                summary="Пример запроса на обновление информации о значении характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "characteristic_name": "Characteristic B",
                    "value": "Updated Value B"
                },
                description="Пример ответа на обновление информации о значении характеристики в Swagger UI",
                summary="Пример ответа на обновление информации о значении характеристики",
                media_type="application/json",
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о значении характеристики",
        summary="Частичное обновление значения характеристики",
        request=CharacteristicValueSerializer,
        responses={200: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name='Partial Update Request Example',
                request_only=True,
                value={
                    "value": "Updated Value B"
                },
                description="Пример запроса на частичное обновление информации о значении характеристики в Swagger UI",
                summary="Пример запроса на частичное обновление информации о значении характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Partial Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "characteristic_name": "Characteristic B",
                    "value": "Updated Value B"
                },
                description="Пример ответа на частичное обновление информации о значении характеристики в Swagger UI",
                summary="Пример ответа на частичное обновление информации о значении характеристики",
                media_type="application/json",
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить значение характеристики",
        summary="Удаление значения характеристики",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
