from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from api.mixins import ActiveQuerysetMixin, IntegrityErrorHandlingMixin
from import_app.models import ImportSetting
from import_app.serializers.model_serializers import ImportSettingSerializer


IMPORT_SETTING_REQUEST_EXAMPLE = {
    "import_task": 1,
    "name": "Импорт товаров",
    "slug": "import-tovarov",
    "fields": {"price": {"id": "ID", "price": "цена"}},
    "path_to_images": "/path/to/images",
    "items_not_in_file_action": "IGNORE",
    "inactive_items_action": "LEAVE",
}
IMPORT_SETTING_RESPONSE_EXAMPLE = {
    "id": 1,
    **IMPORT_SETTING_REQUEST_EXAMPLE,
}
IMPORT_SETTING_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(IMPORT_SETTING_REQUEST_EXAMPLE.items())[:2]}


@extend_schema(
    tags=["Import"],
    parameters=[
        OpenApiParameter(
            name="save_settings",
            description="Сохранить настройки импорта",
            type=bool,
            default=False,
        ),
    ],
)
@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех шаблонов импорта",
        description="Возвращает список всех шаблонов импорта.",
        responses={
            200: OpenApiResponse(
                response=ImportSettingSerializer(many=True),
                description="Список шаблонов импорта успешно получен.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Список шаблонов импорта",
                        value=IMPORT_SETTING_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
    ),
    retrieve=extend_schema(
        summary="Получить информацию о шаблоне импорта",
        description="Возвращает подробную информацию о шаблоне импорта по ID.",
        responses={
            200: OpenApiResponse(
                response=ImportSettingSerializer,
                description="Информация о шаблоне импорта успешно получена.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Информация о шаблоне импорта",
                        value=IMPORT_SETTING_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
    ),
    create=extend_schema(
        summary="Создать новый шаблон импорта",
        description="Создает новый шаблон импорта.",
        request=ImportSettingSerializer,
        responses={
            201: OpenApiResponse(
                response=ImportSettingSerializer,
                description="Шаблон импорта успешно создан.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Шаблон импорта создан",
                        value=IMPORT_SETTING_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary="Шаблон импорта создана",
                value=IMPORT_SETTING_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]

    ),
    update=extend_schema(
        summary="Обновить шаблон импорта",
        description="Обновляет информацию о шаблоне импорта.",
        request=ImportSettingSerializer,
        responses={
            200: OpenApiResponse(
                response=ImportSettingSerializer,
                description="Шаблон импорта успешно обновлен.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Шаблон импорта обновлен",
                        value=IMPORT_SETTING_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary="Шаблон импорта создана",
                value=IMPORT_SETTING_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]

    ),
    partial_update=extend_schema(
        summary="Частично обновить шаблон импорта",
        description="Частично обновляет определенные поля шаблона импорта.",
        request=ImportSettingSerializer,
        responses={
            200: OpenApiResponse(
                response=ImportSettingSerializer,
                description="Шаблон импорта частично обновлен.",
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        summary="Частичное обновление шаблона импорта",
                        value=IMPORT_SETTING_RESPONSE_EXAMPLE,
                    )
                ],
            )
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary="Шаблон импорта создана",
                value=IMPORT_SETTING_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    destroy=extend_schema(
        summary="Удалить шаблон импорта",
        description="Удаляет шаблон импорта по ID.",
        responses={204: OpenApiResponse(description="Шаблон импорта успешно удален.")},
    ),
)
class ImportSettingViewSet(ActiveQuerysetMixin, IntegrityErrorHandlingMixin, ModelViewSet):
    queryset = ImportSetting.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = ImportSettingSerializer
