from typing import Any
from loguru import logger
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import Request


class IntegrityErrorHandlingMixin:
    """
    Mixin для обработки ошибок на уровне dispatch.

    Логирует исключения и возвращает стандартный ответ при непредвиденных ошибках.
    """

    def dispatch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Обрабатывает входящие запросы, добавляя обработку ошибок.

        :param request: HTTP-запрос.
        :type request: Request
        :param args: Дополнительные позиционные аргументы.
        :param kwargs: Дополнительные именованные аргументы.
        :return: Ответ, полученный от базового метода, либо сообщение об ошибке.
        :rtype: Response
        """
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as err:
            logger.exception("An error occurred: {}", err)
            response = Response(
                {"error": "Unexpected server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

            if isinstance(response, Response):
                if not getattr(request, 'accepted_renderer', None):
                    neg = super().perform_content_negotiation(request, force=True)
                    request.accepted_renderer, request.accepted_media_type = neg

            response.accepted_renderer = request.accepted_renderer
            response.accepted_media_type = request.accepted_media_type
            response.renderer_context = super().get_renderer_context()
            return response
