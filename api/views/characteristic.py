from rest_framework import viewsets
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.characteristic import CharacteristicSerializer

from shop.models import Characteristic

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=['Shop']
)
class CharacteristicViewSet(viewsets.ModelViewSet):
    """Возвращает характеристики продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = Characteristic.objects.all().order_by("-created_at")
    serializer_class = CharacteristicSerializer
    permission_classes = [ReadOnlyOrAdminPermission]

    @extend_schema(
        description="Получить список всех характеристик",
        summary="Список характеристик",
        responses={200: CharacteristicSerializer(many=True)},
        examples=[
            OpenApiExample(
                name='List Response Example',
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "name": "Characteristic A",
                        "category": 1
                    },
                    {
                        "id": 2,
                        "name": "Characteristic B",
                        "category": 2
                    },
                    # Добавьте другие характеристики, если есть
                ],
                description="Пример ответа для получения списка всех характеристик в Swagger UI",
                summary="Пример ответа для получения списка всех характеристик",
                media_type="application/json",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретной характеристике",
        summary="Информация о характеристике",
        responses={200: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name='Retrieve Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "name": "Characteristic A",
                    "category": 1
                },
                description="Пример ответа для получения информации о конкретной характеристике в Swagger UI",
                summary="Пример ответа для получения информации о конкретной характеристике",
                media_type="application/json",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Создать новую характеристику",
        summary="Создание характеристики",
        request=CharacteristicSerializer,
        responses={201: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name='Create Request Example',
                request_only=True,
                value={
                    "name": "New Characteristic",
                    "category": 1
                },
                description="Пример запроса на создание новой характеристики в Swagger UI",
                summary="Пример запроса на создание новой характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Create Response Example',
                response_only=True,
                value={
                    "id": 3,
                    "name": "New Characteristic",
                    "category": 1
                },
                description="Пример ответа на создание новой характеристики в Swagger UI",
                summary="Пример ответа на создание новой характеристики",
                media_type="application/json",
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о характеристике",
        summary="Обновление характеристики",
        request=CharacteristicSerializer,
        responses={200: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name='Update Request Example',
                request_only=True,
                value={
                    "name": "Updated Characteristic",
                    "category": 2
                },
                description="Пример запроса на обновление информации о характеристике в Swagger UI",
                summary="Пример запроса на обновление информации о характеристике",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "name": "Updated Characteristic",
                    "category": 2
                },
                description="Пример ответа на обновление информации о характеристике в Swagger UI",
                summary="Пример ответа на обновление информации о характеристике",
                media_type="application/json",
            ),
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о характеристике",
        summary="Частичное обновление характеристики",
        request=CharacteristicSerializer,
        responses={200: CharacteristicSerializer()},
        examples=[
            OpenApiExample(
                name='Partial Update Request Example',
                request_only=True,
                value={
                    "category": 2
                },
                description="Пример запроса на частичное обновление информации о характеристике в Swagger UI",
                summary="Пример запроса на частичное обновление информации о характеристике",
                media_type="application/json",
            ),
            OpenApiExample(
                name='Partial Update Response Example',
                response_only=True,
                value={
                    "id": 1,
                    "name": "Updated Characteristic",
                    "category": 2
                },
                description="Пример ответа на частичное обновление информации о характеристике в Swagger UI",
                summary="Пример ответа на частичное обновление информации о характеристике",
                media_type="application/json",
            ),
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить характеристику",
        summary="Удаление характеристики",
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
