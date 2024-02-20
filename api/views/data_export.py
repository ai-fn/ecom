from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.tasks import export_products_to_csv


class DataExportView(APIView):
    # permission_classes = [permissions.IsAdminUser]
    permission_classes = []

    def get(self, request, format=None):
        data_type = request.query_params.get("type", "PRODUCTS")
        if data_type not in ["PRODUCTS", "BRANDS"]:
            return Response(
                {"error": "Unsupported type parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if data_type == "PRODUCTS":
            # Убедитесь, что пользователь аутентифицирован
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication is required to export products."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Получаем адрес электронной почты пользователя
            user_email = request.user.email

            # Инициируем задачу экспорта в фоне с передачей адреса электронной почты
            task = export_products_to_csv.delay(user_email)
            return JsonResponse(
                {
                    "message": "Export started. You will receive the products file by email."
                }
            )

        return Response(
            {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
        )