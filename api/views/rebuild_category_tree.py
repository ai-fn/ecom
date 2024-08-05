from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAdminUser

from shop.models import Category
from drf_spectacular.utils import extend_schema, OpenApiExample


class RebuildCategoryTreeAPIView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = None

    @extend_schema(
        summary="Восстановление дерева категорий",
        description="Перестроить дерево категорий в базе данных.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "message": "Category tree has been rebuilt successfully"
                },
                response_only=True,
                status_codes=[HTTP_200_OK],
            ),
            OpenApiExample(
                name="Error Response",
                value={
                    "error": "Описание ошибки"
                },
                response_only=True,
                status_codes=[HTTP_400_BAD_REQUEST],
            ),
        ],
    )
    def post(self, request) -> Response:
        try:
            Category.objects.rebuild()
        except Exception as e:
            logger.error(str(e.with_traceback(e.__traceback__)))
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
        
        logger.debug("The category tree has been successfully rebuilt")
        return Response({"message": "Category tree has been rebuilt successfully"}, status=HTTP_200_OK)
