from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

from api.tasks import export_products_to_csv

from drf_spectacular.utils import extend_schema, OpenApiExample


@extend_schema(tags=["Settings"])
class DataExportView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        description="Экспорт товаров",
        summary="Экспорт товаров",
        responses={200: None},
        examples=[
            OpenApiExample(
                name="Delete Request Example",
                request_only=True,
                value=None,
                description="Удаление элемента из корзины",
            ),
            OpenApiExample(
                name="Delete Response Example",
                response_only=True,
                value={
                    "message": "Export started. You will receive the products file by email."
                },
                description="Удаление элемента из корзины",
            ),
        ],
    )
    def get(self, request, format=None):
        data_type = request.query_params.get("type", "PRODUCTS")
        if data_type not in ["PRODUCTS", "BRANDS"]:
            return Response(
                {"error": "Unsupported type parameter."},
                status=HTTP_400_BAD_REQUEST,
            )

        if data_type == "PRODUCTS":

            # Инициируем задачу экспорта в фоне с передачей адреса электронной почты
            export_products_to_csv.delay(request.user.email)
            return JsonResponse(
                {
                    "message": "Export started. You will receive the products file by email."
                }
            )

        return Response(
            {"error": "Invalid request"}, status=HTTP_400_BAD_REQUEST
        )
