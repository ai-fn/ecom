from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    OpenApiExample,
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from import_app.services.import_task_service import ImportTaskService
from import_app.models import ImportTask
from import_app.serializers.model_serializers import ImportTaskSerializer
from shop.models import (
    Brand,
    Category,
    Characteristic,
    CharacteristicValue,
    Price,
    Product,
)

IMPORT_TASK_REQUEST_EXAMPLE = {
    "file": "/media/catalog/import_files/catalog-image-97bc8aab-067d-48ec-86b8-3b334dd70b24.xlsx",
    "user": 1,
    "status": "PENDING",
    "end_at": "2024-06-04T16:57:46.221822+03:00",
    "comment": "Задача на импорт данных",
}
IMPORT_TASK_RESPONSE_EXAMPLE = {
    "id": 1,
**IMPORT_TASK_REQUEST_EXAMPLE,
}
IMPORT_TASK_PARTIAL_UPDATE_REQUEST_EXAMPLE = {k: v for k, v in list(IMPORT_TASK_REQUEST_EXAMPLE.items())[:2]}


@extend_schema(tags=["Import"])
@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех задач импорта",
        description="Возвращает список всех задач импорта.",
        responses={
            HTTP_200_OK: OpenApiResponse(
                response=ImportTaskSerializer(many=True),
                description="Список задач импорта успешно получен.",
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        summary="Список задач",
                        value=IMPORT_TASK_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
    ),
    retrieve=extend_schema(
        summary="Получить информацию о задаче импорта",
        description="Возвращает подробную информацию о задаче импорта по ID.",
        responses={
            HTTP_200_OK: OpenApiResponse(
                response=ImportTaskSerializer,
                description="Информация о задаче импорта успешно получена.",
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        summary="Информация о задаче импорта",
                        value=IMPORT_TASK_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
    ),
    create=extend_schema(
        summary="Создать новую задачу импорта",
        description="Загружает файл и создает новую задачу импорта.",
        request=ImportTaskSerializer,
        responses={
            201: OpenApiResponse(
                response=ImportTaskSerializer,
                description="Задача импорта успешно создана.",
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        summary="Задача импорта создана",
                        value=IMPORT_TASK_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary="Задача импорта создана",
                value=IMPORT_TASK_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    update=extend_schema(
        summary="Обновить задачу импорта",
        description="Обновляет информацию о задаче импорта.",
        request=ImportTaskSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                response=ImportTaskSerializer,
                description="Задача импорта успешно обновлена.",
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        summary="Задача импорта обновлена",
                        value=IMPORT_TASK_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary="Задача импорта создана",
                value=IMPORT_TASK_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Частично обновить задачу импорта",
        description="Частично обновляет определенные поля задачи импорта.",
        request=ImportTaskSerializer,
        responses={
            HTTP_200_OK: OpenApiResponse(
                response=ImportTaskSerializer,
                description="Задача импорта частично обновлена.",
                examples=[
                    OpenApiExample(
                        'Пример успешного ответа',
                        summary="Частичное обновление задачи импорта",
                        value=IMPORT_TASK_RESPONSE_EXAMPLE,
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                'Пример успешного ответа',
                summary="Задача импорта создана",
                value=IMPORT_TASK_PARTIAL_UPDATE_REQUEST_EXAMPLE,
                request_only=True,
            )
        ]
    ),
    destroy=extend_schema(
        summary="Удалить задачу импорта",
        description="Удаляет задачу импорта по ID.",
        responses={
            HTTP_204_NO_CONTENT: OpenApiResponse(
                description="Задача импорта успешно удалена."
            )
        }
    ),
    get_columns=extend_schema(
        summary="Получение названий столбцов из файла",
        description="Получение названий столбцов из файла",
        request=None,
        responses={
            HTTP_200_OK: OpenApiResponse(
                examples=[
                    OpenApiExample(
                        "Успешный ответ",
                        value=[
                            "TITLE",
                            "SKU",
                            "Выбранный цвет",
                            "CATEGORIES",
                            "Размер поддона с лестницами (ДхШхВ), мм",
                            "Прочность сцепления с бетоном",
                            "Максимальная нагрузка",
                            "Длина ступени",
                        ],
                    ),
                ]
            ),
            HTTP_400_BAD_REQUEST: OpenApiResponse(
                examples=[
                    OpenApiExample(
                        "Error Response", value={"error": "Some error message."}
                    ),
                ]
            ),
        },
    ),
    get_all_fields=extend_schema(
        description="Получение доступных полей для всех моделей для импорта",
        summary="Получение доступных полей для всех моделей для импорта",
        examples=[
                OpenApiExample(
                "Response Example",
                value={
                    "fields": {
                        "product": {
                            "id",
                            "title",
                            "category",
                        }
                    }
                },
                response_only=True,
            )
        ]
    ),
)
class ImportTaskViewSet(ModelViewSet):
    queryset = ImportTask.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = ImportTaskSerializer

    @action(detail=True, methods=["GET"], url_path="get-columns")
    def get_columns(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            columns = ImportTaskService.get_columns(instance)
        except Exception as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)

        return Response(columns, status=HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="get-all-fields")
    def get_all_fields(self, request, *args, **kwargs):
        models = (Product, Category, Brand, Price, Characteristic, CharacteristicValue)
        fields = {
            model._meta.model_name: (el.name for el in model._meta.get_fields())
            for model in models
        }

        return Response({"fields": fields}, status=HTTP_200_OK)
