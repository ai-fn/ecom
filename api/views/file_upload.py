import requests
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from api.serializers.setting import SettingSerializer
from api.tasks import handle_csv_file_task, handle_xlsx_file_task
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status


class XlsxFileUploadView(APIView):

    parser_classes = [FileUploadParser]
    queryset = Product.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = None

    @extend_schema(
        description="Импорт товаров",
        summary="Импорт товаров",
        responses={200: None},
        parameters=[
            OpenApiParameter(
                name="type",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Тип данных для импорта (PRODUCTS, BRANDS)",
            ),
        ],
        tags=["Settings"],
    )
    def put(self, request, filename, format=None):
        file_obj = request.data.get("file")
        upload_type = request.query_params.get("type")
        
        r = requests.put(f"http://golang:8080/api/upload/{filename}?type={upload_type}", files={"file": ContentFile(file_obj.read())}, headers={"Authorization": request.headers.get("Authorization")})
        return Response(r.json(), status=r.status_code)
