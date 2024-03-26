from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from api.serializers.setting import SettingSerializer
from rest_framework.permissions import IsAdminUser

from shop.models import Setting, SettingChoices

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(
    tags=["Settings"],
    description="Получение текста robots.txt",
    summary="Получение текста robots.txt",
    examples=[
        OpenApiExample(
            name="Robots Response",
            value={
                "id": 1,
                "type": "string",
                "value_string": "Lorem Ipsum",
                "value_boolean": None,
                "value_number": None,
                "predefined_key": "robots_txt",
                "custom_key": None,
                "value": "Lorem Ipsum",
            },
            response_only=True,
        )
    ],
)
class RobotsTxtView(generics.GenericAPIView):

    serializer_class = SettingSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Setting.objects.all()

    def get(self, request):
        try:
            obj = self.queryset.get(predefined_key=SettingChoices.ROBOTS_TXT)
        except Setting.DoesNotExist:
            return Response(
                {"error": "Настройка для robots.txt не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(obj)
        return Response(serializer.data)


@extend_schema(tags=["Settings"])
class SettingViewSet(viewsets.ModelViewSet):
    """Возвращает настройки

    Args:
        viewsets (_type_): _description_
    """

    queryset = Setting.objects.all().order_by("-created_at")
    serializer_class = SettingSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(
        description="Получить список всех настроек",
        summary="Список настроек",
        responses={200: SettingSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="List Response Example",
                response_only=True,
                value=[
                    {
                        "id": 1,
                        "key": "setting_key_1",
                        "type": "string",
                        "value_string": "setting_value",
                        "value_boolean": True,
                        "value_number": "value",
                        "predefined_key": "predefined_key",
                        "custom_key": "predefined_key",
                    },
                    {
                        "id": 2,
                        "key": "setting_key_2",
                        "type": "string",
                        "value_string": "setting_value",
                        "value_boolean": True,
                        "value_number": "value",
                        "predefined_key": "predefined_key",
                        "custom_key": "predefined_key",
                    },
                ],
                description="Пример ответа для получения списка всех настроек в Swagger UI",
                summary="Пример ответа для получения списка всех настроек",
                media_type="application/json",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Получить информацию о конкретной настройке",
        summary="Информация о настройке",
        responses={200: SettingSerializer()},
        examples=[
            OpenApiExample(
                name="Retrieve Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "key": "setting_key_1",
                    "type": "string",
                    "value_string": "setting_value",
                    "value_boolean": True,
                    "value_number": "value",
                    "predefined_key": "predefined_key",
                    "custom_key": "predefined_key",
                },
                description="Пример ответа для получения информации о конкретной настройке в Swagger UI",
                summary="Пример ответа для получения информации о конкретной настройке",
                media_type="application/json",
            ),
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Создать новую настройку",
        summary="Создание настройки",
        request=SettingSerializer,
        responses={201: SettingSerializer()},
        examples=[
            OpenApiExample(
                name="Create Request Example",
                request_only=True,
                value={
                    "key": "setting_key_1",
                    "type": "string",
                    "value_string": "setting_value",
                    "value_boolean": True,
                    "value_number": "value",
                    "predefined_key": "predefined_key",
                    "custom_key": "predefined_key",
                },
                description="Пример запроса на создание новой настройки в Swagger UI",
                summary="Пример запроса на создание новой настройки",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Create Response Example",
                response_only=True,
                value={
                    "id": 3,
                    "key": "setting_key_3",
                    "type": "string",
                    "value_string": "setting_value",
                    "value_boolean": True,
                    "value_number": "value",
                    "predefined_key": "predefined_key",
                    "custom_key": "predefined_key",
                },
                description="Пример ответа на создание новой настройки в Swagger UI",
                summary="Пример ответа на создание новой настройки",
                media_type="application/json",
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Обновить информацию о конкретной настройке",
        summary="Обновление настройки",
        request=SettingSerializer,
        responses={200: SettingSerializer()},
        examples=[
            OpenApiExample(
                name="Update Request Example",
                request_only=True,
                value={"type": "string", "value_string": "updated_value"},
                description="Пример запроса на обновление информации о конкретной настройке в Swagger UI",
                summary="Пример запроса на обновление информации о конкретной настройке",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Update Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "key": "setting_key_3",
                    "type": "string",
                    "value_string": "setting_value",
                    "value_boolean": True,
                    "value_number": "value",
                    "predefined_key": "predefined_key",
                    "custom_key": "predefined_key",
                },
                description="Пример ответа на обновление информации о конкретной настройке в Swagger UI",
                summary="Пример ответа на обновление информации о конкретной настройке",
                media_type="application/json",
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Удалить настройку",
        summary="Удаление настройки",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        description="Частично обновить информацию о конкретной настройке",
        summary="Частичное обновление настройки",
        request=SettingSerializer,
        responses={200: SettingSerializer()},
        examples=[
            OpenApiExample(
                name="Partial Update Request Example",
                request_only=True,
                value={"value_string": "partial_update_value"},
                description="Пример запроса на частичное обновление информации о конкретной настройке в Swagger UI",
                summary="Пример запроса на частичное обновление информации о конкретной настройке",
                media_type="application/json",
            ),
            OpenApiExample(
                name="Partial Update Response Example",
                response_only=True,
                value={
                    "id": 1,
                    "key": "setting_key_3",
                    "type": "string",
                    "value_string": "partial_update_value",
                    "value_boolean": True,
                    "value_number": "value",
                    "predefined_key": "predefined_key",
                    "custom_key": "predefined_key",
                },
                description="Пример ответа на частичное обновление информации о конкретной настройке в Swagger UI",
                summary="Пример ответа на частичное обновление информации о конкретной настройке",
                media_type="application/json",
            ),
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
