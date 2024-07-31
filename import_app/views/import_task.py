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
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

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


@extend_schema(tags=["Import"])
@extend_schema_view(
    upload_file=extend_schema(
        summary="Загрузка файла",
        description="Загрузка файла",
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
