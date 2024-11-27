import time
import requests
from loguru import logger
from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response
from account.actions import SendCodeBaseAction


class SendCodeToTelegramAction(SendCodeBaseAction):
    """
    Класс для отправки кода подтверждения через Telegram.

    Использует Telegram Bot API для отправки сообщения в указанный чат. Требуются токен бота 
    и идентификатор чата, которые должны быть указаны в настройках Django.
    """

    api_key = getattr(settings, "SMS_RU_TOKEN")
    bot_token = getattr(settings, "TG_BOT_TOKEN")
    chat_id = getattr(settings, "CHAT_ID")
    link = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def _send_message(self, request, code: str, cache_key: str) -> Response:
        """
        Отправляет сообщение с кодом подтверждения в указанный Telegram-чат.

        :param request: HTTP-запрос, содержащий информацию о пользователе.
        :type request: HttpRequest
        :param code: Код подтверждения, который нужно отправить.
        :type code: str
        :param cache_key: Ключ для сохранения кода в кэше.
        :type cache_key: str
        :return: Возвращает ``True``, если сообщение успешно отправлено, иначе ``False``.
        :rtype: bool
        """

        tg_params = {
            "chat_id": self.chat_id,
            "text": self.message.format(code=code),
            "json": 1,
        }

        response = requests.post(self.link, params=tg_params)
        response_data = response.json()
        if response_data.get("ok"):
            et = time.time() + self.remaining_time
            cache.set(
                cache_key,
                {
                    "expiration_time": et,
                    "code": code,
                },
                timeout=self.code_lifetime,
            )
            return True
        else:
            logger.error(
                "status_text",
                "%s: %s"
                % (
                    response_data.get("error_code"),
                    response_data.get("description"),
                ),
            )
            return False
