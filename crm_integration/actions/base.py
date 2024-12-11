from typing import Any, Dict
from abc import ABC, abstractmethod

from django.http import HttpRequest


class BaseAction(ABC):
    """
    Базовый класс события CRM системы.
    """

    @abstractmethod
    def execute(self, data: Dict[str, Any]):
        pass


class BaseWebhookHandler(ABC):
    """
    Базовый класс обработчика вебхука CRM системы.
    """

    @abstractmethod
    def handle(self, request: HttpRequest) -> None:
        pass
