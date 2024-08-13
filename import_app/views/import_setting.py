import os

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from import_app.tasks import handle_file_task
from import_app.models import ImportSetting
from import_app.serializers.model_serializers import ImportSettingSerializer

from import_app.views.import_task import IMPORT_TASK_RESPONSE_EXAMPLE


IMPORT_SETTING_REQUEST_EXAMPLE = {
    "import_task": 1,
    "name": "Импорт товаров",
    "slug": "import-tovarov",
    "fields": {"id": "ID", "price": "цена"},
    "path_to_images": "/path/to/images",
    "items_not_in_file_action": "IGNORE",
    "inactive_items_action": "LEAVE",
    "remove_existing_price_if_empty": False,
}
IMPORT_SETTING_RESPONSE_EXAMPLE = {
    "id": 1,
    **IMPORT_SETTING_REQUEST_EXAMPLE,
    "import_task": IMPORT_TASK_RESPONSE_EXAMPLE,
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
    start_import=extend_schema(
        description="Запуск импорта",
        summary="Запуск импорта",
        examples=[
            OpenApiExample(
                "Request Example",
                value=IMPORT_SETTING_REQUEST_EXAMPLE,
                request_only=True,
            ),
            OpenApiExample(
                "Response Example",
                value={"detail": "import started with settigs: {import settings}"},
                response_only=True,
            )
        ]
    ),
)
class ImportSettingViewSet(ModelViewSet):
    queryset = ImportSetting.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = ImportSettingSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["save_settings"] = (
            self.request.query_params.get("save_settings") == "true"
        )
        return context

    @action(detail=False, methods=["POST"], url_path="start-import")
    def start_import(self, request, *args, **kwargs):
        save_settings = request.query_params.get("save_settings") == "true"

        serializer: ImportSettingSerializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        if save_settings:
            serializer.save()

        import_task = serializer.validated_data["import_task"]

        _, format = os.path.splitext(import_task.file.name)
        if format != ".xlsx":
            return Response(
                {"detail": "File object must be in .xlsx format."},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            handle_file_task.delay(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": f"import started with settigs: {serializer.data}"},
            status=HTTP_200_OK,
        )
