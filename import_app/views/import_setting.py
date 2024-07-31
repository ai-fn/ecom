import os

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from import_app.tasks import handle_file_task
from import_app.models import ImportSetting
from import_app.serializers.model_serializers import ImportSettingSerializer


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
@extend_schema_view()
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
