import time
from typing import Any, Dict

from django.conf import settings


class TokenExpiredTimeMixin:
    """
    Mixin для добавления времени истечения срока действия токенов в данные ответа.

    Добавляет поля `access_expired_at` и `refresh_expired_at` с указанием времени истечения
    срока действия access и refresh токенов соответственно.
    """

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        """
        Валидирует входящие данные и добавляет информацию о времени истечения токенов.

        :param attrs: Входящие данные для валидации.
        :type attrs: Dict[str, Any]
        :return: Данные с добавленной информацией о времени истечения токенов.
        :rtype: Dict[str, str]
        """
        data = super().validate(attrs)
        data = self._set_time_fields(data)
        return data

    @staticmethod
    def _set_time_fields(data: dict) -> dict:
        """
        Добавляет поля `access_expired_at` и `refresh_expired_at` в данные.

        :param data: Данные для модификации.
        :type data: dict
        :return: Модифицированные данные с добавленными полями времени истечения.
        :rtype: dict
        """
        data["access_expired_at"] = (
            time.time() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        )
        data["refresh_expired_at"] = (
            time.time() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        )
        return data
