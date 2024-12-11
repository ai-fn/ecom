from typing import Any, Dict
from loguru import logger
from django.http import HttpRequest
from crm_integration.actions import BaseWebhookHandler
from crm_integration.adapters import CRMAdapter, OrderCRMAdapter
from crm_integration.actions.bitrix import (
    ValidateRequestAction,
    CreateOrderAction,
)


def handle_error(func):
    def _wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as err:
            logger.error(
                f"Error while executing crm action '{func.__qualname__}': {err}."
            )

    return _wrapper


class BitrixAPI(
    OrderCRMAdapter,
    CRMAdapter,
):
    """Класс-адаптер для CRM системы bitrix.

    Этот класс обрабатывает входящие события и адаптирует их для использования в системе.

    Attributes:
        INCOMING_ACTIONS (Dict[str, Dict[str, BaseWebhookHandler]]):
            Словарь, который определяет, какие события обрабатываются адаптером.
            Ключи верхнего уровня представляют собой названия моделей (например, "customerorders"),
            а значения — словари, где ключи — это названия методов (например, "upd", "add"),
            а значения — классы обработчиков событий, которые будут вызваны для обработки
            соответствующих событий. Это позволяет адаптеру динамически обрабатывать
            различные типы событий в зависимости от их источника.
    """

    INCOMING_ACTIONS: Dict[str, Dict[str, BaseWebhookHandler]] = {}


    @handle_error
    def validate_request(self, request: HttpRequest) -> bool:
        """
        Метод валидации входящего запроса вебхука.

        Проверяет, соответствует ли входящий запрос требованиям валидации.

        Args:
            request (HttpRequest): Входящий HTTP запрос, который необходимо проверить.

        Returns:
            bool: True, если запрос валиден, иначе False.
        """
        return ValidateRequestAction().handle(request)

    @handle_error
    def handle_incoming_webhook(self, request: HttpRequest) -> None:
        """
        Метод обработки входящего запроса вебхука.

        Обрабатывает входящий запрос, проверяет его на валидность и вызывает соответствующий
        обработчик события на основе модели и действия, указанных в запросе.

        Args:
            request (HttpRequest): Входящий HTTP запрос вебхука.
        """
        if not self.validate_request(request):
            logger.warning(f"Invalid webhook request: {request.path}")
            return

        model_name = request.POST["model"]
        action_name = request.POST["action"]

        model_actions = self.INCOMING_ACTIONS.get(model_name)

        if not model_actions:
            logger.warning(f"Trying to call unknown model '{model_name}'.")
            return

        handler_class = model_actions.get(action_name)

        if not handler_class:
            logger.warning(
                f"Trying to call unknown action '{action_name}' for model '{model_name}'."
            )
            return

        handler: BaseWebhookHandler = handler_class()
        handler.handle(request)

    @handle_error
    def crm_create_order(self, data: Dict[str, Any]) -> None:
        """
        Метод создания заказа в CRM системе.

        Создает новый заказ в CRM, используя предоставленные данные.

        Args:
            data (Dict[str, Any]): Данные, необходимые для создания заказа.
        """
        return CreateOrderAction().execute(data)
