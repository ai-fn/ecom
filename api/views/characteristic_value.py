from rest_framework.viewsets import ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample

from api.filters import CharacteristicValueFilters
from api.permissions import ReadOnlyOrAdminPermission
from api.serializers.characteristic_value import CharacteristicValueSerializer
from api.mixins import IntegrityErrorHandlingMixin, ActiveQuerysetMixin

from shop.models import CharacteristicValue


CHARACTERISTIC_VALUE_REQUEST_EXAMPLE = {
    "characteristic_name": "Применение",
    "value": "Применяется для защиты теплоизоляционного слоя в системах скатных кровель, стен каркасной конструкции и вентилируемых фасадов от вредного воздействия воды, ветра, пыли. Используется в конструкциях с однослойной вентиляцией, монтируется непосредственно на утеплитель или сплошной настил. Может использоваться в качестве временной кровли до 6 месяцев.",
    "slug": "primeniaetsia-dlia-zashchity-teploizoliatsionnogo-sloia-v-sistemakh-skatnykh-krovel-sten-karkasnoi-konstruktsii-i-ventiliruemykh-fasadov-ot-vrednogo-vozdeistviia-vody-vetra-pyli-ispol-zuetsia-v-konstruktsiiakh-s-odnosloinoi-ventiliatsiei-montiruetsia-neposredstvenno-na-uteplitel-ili-sploshnoi-nastil-mozhet-ispol-zovat-sia-v-kachestve-vremennoi-krovli-do-6-mesiatsev",
    "characteristic_id": 1,
    "product_id": 1,
    "is_active": True,
}
CHARACTERISTIC_VALUE_RESPONSE_EXAMPLE = {
    "id": 67909,
    **CHARACTERISTIC_VALUE_REQUEST_EXAMPLE,
}
CHARACTERISTIC_PARTIAL_UPDATE_REQUEST_EXAMPLE = {
    k: v for k, v in list(CHARACTERISTIC_VALUE_REQUEST_EXAMPLE.items())[:2]
}

@extend_schema_view(
    list=extend_schema(
        description="Получить список всех значений характеристик",
        summary="Список значений характеристик",
        responses={200: CharacteristicValueSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=CHARACTERISTIC_VALUE_RESPONSE_EXAMPLE,
                description="Пример ответа для получения списка всех значений характеристик в Swagger UI",
                summary="Пример ответа для получения списка всех значений характеристик",
                media_type="application/json",
            ),
        ],
    ),
    create=extend_schema(
        description="Создать новое значение характеристики",
        summary="Создание значения характеристики",
        request=CharacteristicValueSerializer,
        responses={201: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value=CHARACTERISTIC_VALUE_REQUEST_EXAMPLE,
                description="Пример запроса на создание нового значения характеристики в Swagger UI",
                summary="Пример запроса на создание нового значения характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value=CHARACTERISTIC_VALUE_RESPONSE_EXAMPLE,
                description="Пример ответа на создание нового значения характеристики в Swagger UI",
                summary="Пример ответа на создание нового значения характеристики",
                media_type="application/json",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Получить информацию о конкретном значении характеристики",
        summary="Информация о значении характеристики",
        responses={200: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value=CHARACTERISTIC_VALUE_RESPONSE_EXAMPLE,
                description="Пример ответа для получения информации о конкретном значении характеристики в Swagger UI",
                summary="Пример ответа для получения информации о конкретном значении характеристики",
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        description="Обновить информацию о значении характеристики",
        summary="Обновление значения характеристики",
        request=CharacteristicValueSerializer,
        responses={200: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value=CHARACTERISTIC_VALUE_REQUEST_EXAMPLE,
                description="Пример запроса на обновление информации о значении характеристики в Swagger UI",
                summary="Пример запроса на обновление информации о значении характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value=CHARACTERISTIC_VALUE_RESPONSE_EXAMPLE,
                description="Пример ответа на обновление информации о значении характеристики в Swagger UI",
                summary="Пример ответа на обновление информации о значении характеристики",
                media_type="application/json",
            ),
        ],
    ),
    partial_update=extend_schema(
        description="Частично обновить информацию о значении характеристики",
        summary="Частичное обновление значения характеристики",
        request=CharacteristicValueSerializer,
        responses={200: CharacteristicValueSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value=CHARACTERISTIC_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                description="Пример запроса на частичное обновление информации о значении характеристики в Swagger UI",
                summary="Пример запроса на частичное обновление информации о значении характеристики",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value=CHARACTERISTIC_VALUE_RESPONSE_EXAMPLE,
                description="Пример ответа на частичное обновление информации о значении характеристики в Swagger UI",
                summary="Пример ответа на частичное обновление информации о значении характеристики",
                media_type="application/json",
            ),
        ],
    ),
    destroy=extend_schema(
        description="Удалить значение характеристики",
        summary="Удаление значения характеристики",
        responses={204: None},
    ),
)
@extend_schema(
    tags=["Shop"],
)
class CharacteristicValueViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    """Возвращает значение характеристик продукта

    Args:
        viewsets (_type_): _description_
    """

    queryset = CharacteristicValue.objects.order_by("-created_at")
    serializer_class = CharacteristicValueSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CharacteristicValueFilters
