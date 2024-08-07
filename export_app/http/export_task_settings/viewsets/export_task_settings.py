from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse

from export_app.models import ExportSettings
from export_app.http.export_task_settings.serializers import ExportSettingsSerializer
from export_app.http.export_task_settings.examples import *


@extend_schema_view(
    list=extend_schema(
        summary='Список всех настроек экспорта',
        description='Получить список всех настроек экспорта.',
        responses={
            200: OpenApiResponse(
                response=ExportSettingsSerializer(many=True),
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value=example_export_settings_successful_response
                    )
                ]
            )
        }
    ),
    retrieve=extend_schema(
        summary='Получить настройки экспорта',
        description='Получить детали конкретных настроек экспорта по ID.',
        responses={
            200: OpenApiResponse(
                response=ExportSettingsSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value=example_export_settings_successful_response
                    )
                ]
            )
        }
    ),
    create=extend_schema(
        summary='Создать новые настройки экспорта',
        description='Создать новые настройки экспорта.',
        request=ExportSettingsSerializer,
        examples=[
            OpenApiExample(
                'Пример запроса',
                value=example_export_settings_create_request
            )
        ],
        responses={
            201: OpenApiResponse(
                response=ExportSettingsSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value=example_export_settings_successful_response
                    )
                ]
            )
        }
    ),
    update=extend_schema(
        summary='Обновить настройки экспорта',
        description='Обновить детали конкретных настроек экспорта.',
        request=ExportSettingsSerializer,
        examples=[
            OpenApiExample(
                'Пример запроса',
                value=example_export_settings_create_request
            )
        ],
        responses={
            200: OpenApiResponse(
                response=ExportSettingsSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value=example_export_settings_successful_response
                    )
                ]
            )
        }
    ),
    partial_update=extend_schema(
        summary='Частично обновить настройки экспорта',
        description='Частично обновить детали конкретных настроек экспорта.',
        request=ExportSettingsSerializer,
        examples=[
            OpenApiExample(
                'Пример запроса',
                value=example_export_settings_create_request
            )
        ],
        responses={
            200: OpenApiResponse(
                response=ExportSettingsSerializer,
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        value=example_export_settings_successful_response
                    )
                ]
            )
        }
    ),
    destroy=extend_schema(
        summary='Удалить настройки экспорта',
        description='Удалить конкретные настройки экспорта.',
        responses={
            204: OpenApiResponse(
                response=None,
                examples=[
                    OpenApiExample(
                        'Пример успешного удаления',
                        value=None
                    )
                ]
            )
        }
    )
)
@extend_schema(
    tags=["Export App"],
)
class ExportSettingsViewSet(ModelViewSet):
    serializer_class = ExportSettingsSerializer
    queryset = ExportSettings.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if save_settings := self.request.query_params.get("save_settings"):
            context["save_settings"] = save_settings

        return context
