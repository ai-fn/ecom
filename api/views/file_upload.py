import os
import requests
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from shop.models import Product
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import NoReverseMatch, reverse
from rest_framework.response import Response


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

        host = os.environ.get("GO_HOST", "golang")
        port = os.environ.get("GO_PORT", "8080")

        if file_obj is None:
            return Response({"error": "File object is requeire"})

        if upload_type is None:
            return Response({"error": "Type parametr is required"})

        try:
            path = reverse("api:upload_products", kwargs={"filename": filename})
        except NoReverseMatch:
            path = f"/api/upload/{filename}"

        r = requests.put(
            f"http://{host}:{port}{path}?type={upload_type}",
            files={"file": ContentFile(file_obj.read())},
            headers={"Authorization": request.headers.get("Authorization")},
        )
        return Response(r.json(), status=r.status_code)
