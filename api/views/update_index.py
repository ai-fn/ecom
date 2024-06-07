import sys
from django.http import JsonResponse
from django.core.management import call_command
from django.core.management.base import CommandError

from loguru import logger
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.decorators import closed_view


class UpdateIndex(APIView):
    permission_classes = [AllowAny]
    serializer_class = None

    @extend_schema(
        summary="Обновление индексов Elasticsearch",
        description="Запуск команды обновления индексов в Elasticsearch.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": "success",
                    "message": "Successfully updated Elasticsearch indexes"
                },
                response_only=True,
                status_codes=[HTTP_200_OK],
            ),
        ],
    )
    @closed_view
    def post(self, request, *args, **kwargs):
        try:
            call_command('update_index')
            return JsonResponse({'status': 'success', 'message': 'Successfully updated Elasticsearch indexes'}, status=HTTP_200_OK)
        except CommandError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(str(e.with_traceback(e.__traceback__)))
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
