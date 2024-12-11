from typing import Any, Dict
from django.http import HttpRequest
from abc import ABCMeta, abstractmethod


class CRMMeta(ABCMeta):
    """Метакласс для регистрации CRM адаптеров.

    Этот метакласс регистрирует все классы, которые используют его в качестве метакласса.
    """
    _register_crm: dict[str, "CRMAdapter"] = {}

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any
    ):
        """Создает новый класс и регистрирует его.

        Args:
            mcls: Метакласс.
            name: Имя нового класса.
            bases: Кортеж базовых классов.
            namespace: Пространство имен нового класса.
            **kwargs: Дополнительные аргументы.

        Returns:
            Новый класс.
        """
        new_class = super().__new__(mcls, name, bases, namespace, **kwargs)
        
        if bases:
            mcls._register_crm.setdefault(new_class.__name__.lower(), new_class)

        return new_class


class CRMAdapter(metaclass=CRMMeta):
    """Абстрактный базовый класс для CRM адаптеров.

    Этот класс определяет интерфейс для обработки входящих вебхуков.
    """

    @abstractmethod
    def handle_incoming_webhook(self, request: HttpRequest) -> Dict[str, Any]:
        """Обрабатывает входящий вебхук.

        Args:
            request: HTTP запрос.

        Returns:
            Словарь с данными, полученными из вебхука.
        """
        pass


class OrderCRMAdapter(CRMAdapter):
    """Адаптер для обработки заказов в CRM."""

    @abstractmethod
    def crm_create_order(self, data: Dict[str, Any]):
        """Создает заказ в CRM.

        Args:
            data: Данные заказа.
        """
        pass


class UserCRMAdapter(CRMAdapter):
    """Адаптер для обработки пользователей в CRM."""

    @abstractmethod
    def crm_create_user(self, data: Dict[str, Any]):
        """Создает пользователя в CRM.

        Args:
            data: Данные пользователя.
        """
        pass
