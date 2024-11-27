import requests
from loguru import logger
from rest_framework.response import Response
from account.actions import SendCodeBaseAction
from django.conf import settings


class SendCodeToSmsAction(SendCodeBaseAction):
    """
    Класс для отправки кода подтверждения через SMS.

    Использует внешний сервис SMS.ru для отправки сообщений. Подключение осуществляется
    с использованием API-ключа, указанного в настройках Django.
    """

    link = "https://sms.ru/sms/send"
    api_key = getattr(settings, "SMS_RU_TOKEN")

    def _send_message(self, request, code: str, *args, **kwargs) -> Response:
        """
        Отправляет SMS с кодом подтверждения на указанный номер телефона.

        :param request: HTTP-запрос, содержащий информацию о пользователе.
        :type request: HttpRequest
        :param code: Код подтверждения, который нужно отправить.
        :type code: str
        :return: Возвращает ``True``, если SMS было отправлено успешно, иначе ``False``.
        :rtype: bool
        """

        sms_params = {
            "api_id": self.api_key,
            "to": self.kwargs[self.lookup_field],
            "msg": self.message.format(code=code),
            "json": 1,
        }
        response = requests.get(self.link, params=sms_params)
        response_data = response.json()
        if response_data.get("status") == "OK":
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
