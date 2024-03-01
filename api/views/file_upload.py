from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from api.tasks import handle_csv_file_task, handle_xlsx_file_task
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status


class XlsxFileUploadView(APIView):
    parser_classes = [FileUploadParser]
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]
    # permission_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Тип данных для импорта (PRODUCTS, BRANDS)",
            ),
        ]
    )
    def put(self, request, filename, format=None):
        file_obj = request.data["file"]
        upload_type = request.query_params.get("type")

        file_name = default_storage.save(
            "tmp/" + filename, ContentFile(file_obj.read())
        )
        file_path = default_storage.path(file_name)

        # Проверка на поддерживаемые типы
        if upload_type not in ["PRODUCTS", "BRANDS"]:
            return Response(
                {"error": "Unsupported type parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if filename.endswith(".xlsx"):
            result = handle_xlsx_file_task.delay(file_path, upload_type)
        elif filename.endswith(".csv"):
            result = handle_csv_file_task.delay(file_path, upload_type)
        else:
            return Response(
                {"error": "Unsupported file format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not result:
            return Response(
                {"error": "Error processing file."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
        return Response({'result': result.get()}, status=status.HTTP_200_OK)
