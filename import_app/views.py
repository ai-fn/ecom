import os
from loguru import logger

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from import_app.tasks import handle_xlsx_file_task
from import_app.models import ImportTask, ImportSetting
from import_app.serializers import (
    ImportTaskSerializer,
    ImportSettingSerializer
)


@extend_schema(tags=["Import"])
@extend_schema_view(
    upload_file=extend_schema(
        summary="Загрузка файла",
        description="Загрузка файла",
    )
)
class ImportTaskViewSet(ModelViewSet):
    queryset = ImportTask.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = ImportTaskSerializer


@extend_schema(
    tags=["Import"],
    parameters=[
        OpenApiParameter(
            name="save_settings",
            description="Сохранить настройки импорта",
            type=bool,
            default=False,
        ),
    ]
)
@extend_schema_view()
class ImportSettingViewSet(ModelViewSet):
    queryset = ImportSetting.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = ImportSettingSerializer

    @action(detail=False, methods=["POST"], url_path="start-import")
    def start_import(self, request, *args, **kwargs):
        save_settings = request.query_params.get("save_settigs", "false") == "true"

        serializer: ImportSettingSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if save_settings:
            serializer.save()
        
        import_task = serializer.validated_data["import_task"]

        _, format = os.path.splitext(import_task.file.name)
        if format != ".xlsx":
            return Response({"detail": "File object must be in .xlsx format."}, status=HTTP_400_BAD_REQUEST)
        
        handle_xlsx_file_task.delay(import_task.id, "PRODUCTS")

        return Response({"detail": f"import started with settigs: {serializer.data}"}, status=HTTP_200_OK)
