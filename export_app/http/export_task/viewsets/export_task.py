from loguru import logger

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)

from export_app.http.export_task_settings.serializers.export_task_settings import ExportSettingsSerializer
from export_app.models import ExportSettings, ExportTask
from export_app.http.export_task.serializers import ExportTaskSerializer
from export_app.tasks import export
from export_app.http.export_task.examples import *

request_example = OpenApiExample(
    "Пример запроса", value=example_create_request, request_only=True
)

start_export_parameters = [
    OpenApiParameter(
        name="mail_to",
        description="Почта для получения файла экспорта",
        type=str,
        required=False,
    ),
    OpenApiParameter(
        name="file_type",
        description="Расширение файла",
        required=True,
        type=str,
        enum=[".xlsx", ".csv"],
    ),
    OpenApiParameter(
        name="setting_slug",
        description="Слаг настроек для начала экспорта",
        type=str,
        required=False,
    )
]

start_export_responses = {
    400: OpenApiResponse(
        response=ExportTaskSerializer,
        examples=[
            OpenApiExample(
                "Пример ошибки",
                value=example_invalid_file_type_response,
            ),
        ],
    ),
    200: OpenApiResponse(
        response=ExportTaskSerializer,
        examples=[
            OpenApiExample(
                "Пример успешного начала импорта",
                value=example_start_task_export_response,
            )
        ],
    ),
}


@extend_schema_view(
    list=extend_schema(
        summary="Список всех задач экспорта",
        description="Получить список всех задач экспорта.",
        responses={
            200: OpenApiResponse(
                response=ExportTaskSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=[
                            example_successful_response_completed,
                            example_successful_response_pending,
                        ],
                    )
                ],
            )
        },
    ),
    retrieve=extend_schema(
        summary="Получить задачу экспорта",
        description="Получить детали конкретной задачи экспорта по ID.",
        responses={
            200: OpenApiResponse(
                response=ExportTaskSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=example_successful_response_pending,
                    )
                ],
            )
        },
    ),
    create=extend_schema(
        summary="Создать новую задачу экспорта",
        description="Создать новую задачу экспорта.",
        request=ExportTaskSerializer,
        examples=[request_example],
        responses={
            201: OpenApiResponse(
                response=ExportTaskSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=example_successful_response_pending,
                    )
                ],
            )
        },
    ),
    update=extend_schema(
        summary="Обновить задачу экспорта",
        description="Обновить детали конкретной задачи экспорта.",
        request=ExportTaskSerializer,
        examples=[request_example],
        responses={
            200: OpenApiResponse(
                response=ExportTaskSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=example_successful_response_pending,
                    )
                ],
            )
        },
    ),
    partial_update=extend_schema(
        summary="Частично обновить задачу экспорта",
        description="Частично обновить детали конкретной задачи экспорта.",
        request=ExportTaskSerializer,
        examples=[request_example],
        responses={
            200: OpenApiResponse(
                response=ExportTaskSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=example_successful_response_pending,
                    )
                ],
            )
        },
    ),
    destroy=extend_schema(
        summary="Удалить задачу экспорта",
        description="Удалить конкретную задачу экспорта.",
        responses={
            204: OpenApiResponse(
                response=None,
                examples=[OpenApiExample("Пример успешного удаления", value=None)],
            )
        },
    ),
    get_allowed_models=extend_schema(
        summary="Получение имён доступных моделей",
        description="Получение имён доступных моделей",
        parameters=[OpenApiParameter(name="model", type=str, required=True)],
        responses={
            200: OpenApiResponse(
                response=ExportTaskSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного получения доступных моделей",
                        value=example_model_names_response,
                    ),
                ],
            )
        },
    ),
    get_allowed_model_fields=extend_schema(
        summary="Получение имён доступных полей для модели",
        description="Получение имён доступных полей для модели",
        parameters=[
            OpenApiParameter(
                name="model",
                type=str,
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=ExportTaskSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного получения доступных полей модели",
                        value=examle_model_fields_response,
                    ),
                ],
            )
        },
    ),
    get_all=extend_schema(
        summary="Получение имён доступных полей для всех моделей для экспорта",
        description="Получение имён доступных полей для всех моделей для экспорта",
        request=ExportTaskSerializer,
        responses={
            200: OpenApiResponse(
                response=ExportTaskSerializer,
                examples=[
                    OpenApiExample(
                        "Пример успешного ответа",
                        value=example_get_all_response,
                    )
                ],
            )
        },
    ),
    start_export=extend_schema(
        summary="Начало экспорта",
        description="Начало экспорта",
        parameters=start_export_parameters,
        responses=start_export_responses,
        operation_id="api_export_app_export_tasks_start_export",
    ),
    start_export_obj=extend_schema(
        summary="Начало экспорта",
        description="Начало экспорта",
        parameters=start_export_parameters,
        responses=start_export_responses,
    ),
)
@extend_schema(tags=["Export App"])
class ExportTaskViewSet(ModelViewSet):
    serializer_class = ExportTaskSerializer
    queryset = ExportTask.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["save_settings"] = self.request.query_params.get("save_settings", "false").lower() == "true"
        return context

    @action(detail=False, methods=["GET"], url_path="allowed-models")
    def get_allowed_models(self, request, *args, **kwargs):
        result = ContentType.objects.filter(
            app_label__in=settings.IMPORT_EXPORT_APPS
        ).values_list("model", flat=True)
        return Response({"result": result}, status=HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="model-fields")
    def get_allowed_model_fields(self, request, *args, **kwargs):
        model_name = request.query_params.get("model")
        if not model_name:
            return Response(
                {"detail": "Parameter 'model' is required"}, status=HTTP_400_BAD_REQUEST
            )

        ct = ContentType.objects.filter(
            app_label__in=settings.IMPORT_EXPORT_APPS, model=model_name
        ).first()
        if not ct:
            return Response({"detail": f"Model with name '{model_name}' not found."})

        result = [field.name for field in ct.model_class()._meta.get_fields()]

        return Response({"result": result}, status=HTTP_200_OK)

    def start(self, request, instance=None) -> Response:
        file_type = request.query_params.get("file_type", ".xlsx")

        if file_type not in (".xlsx", ".csv"):
            return Response(
                {
                    "error": f"Invalid file type: expected (.xlsx, .csv), got ({file_type})"
                },
                status=HTTP_400_BAD_REQUEST,
            )
        
        task_settings = None
        mail_to = request.query_params.get("mail_to")
        settings_slug = request.query_params.get("setting_slug")
        setting = ExportSettings.objects.filter(slug=settings_slug).first()

        if not instance:
            data = request.data
            if setting:
                data["settings"] = ExportSettingsSerializer(instance=setting).data

            serializer = self.get_serializer(data=data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

            task_settings = serializer.validated_data.get("settings")
            if not task_settings:
                return Response(
                    {"error": "Could not start export without settigns"},
                    status=HTTP_400_BAD_REQUEST,
                )

            instance = serializer.save()
            serializer_data = self.get_serializer(instance=instance).data
            settings_data = serializer.initial_data['settings']
            data = {**serializer_data, "settings": settings_data}
        else:
            if setting:
                instance.settings = task_settings
            
            task_settings = instance.settings.name
            data = self.get_serializer(instance=instance).data

        export.delay(data, file_type, mail_to)
        message = f"Export task started with settings '{task_settings}'"
        logger.info(message)

        return Response({"detail": message}, status=HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="save_settings",
                type=bool,
                default=False,
            )
        ],
    )
    @action(detail=False, methods=["POST"], url_path="start-export")
    def start_export(self, request, *args, **kwargs):
        response = self.start(request)
        return response

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="save_settings",
                type=bool,
                default=False,
            )
        ],
    )
    @action(detail=True, methods=["POST"], url_path="start-export")
    def start_export_obj(self, request, *args, **kwargs):
        task = self.get_object()
        response = self.start(request, instance=task)
        return response

    @action(detail=False, methods=["GET"], url_path="get-all")
    def get_all(self, request, *args, **kwargs):
        cts = ContentType.objects.filter(app_label__in=settings.IMPORT_EXPORT_APPS)
        data = dict()
        for ct in cts:
            model = ct.model_class()
            if model is not None:

                data[ct.model] = [field.name for field in model._meta.get_fields()]

        return Response({"result": data}, status=HTTP_200_OK)
