from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny

from api.decorators import closed_view
from shop.models import Category


class RebuildCategoryTreeAPIView(APIView):
    permission_classes = [AllowAny]

    @closed_view
    def post(self, request) -> Response:
        try:
            Category.objects.rebuild()
        except Exception as e:
            logger.error(str(e.with_traceback(e.__traceback__)))
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
        
        logger.debug("The category tree has been successfully rebuilt")
        return Response({"message": "Category tree has been rebuilt successfully"}, status=HTTP_200_OK)
