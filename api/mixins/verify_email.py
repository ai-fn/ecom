import time
from typing import Optional
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from shop.services import EmailService
from shop.utils import get_base_domain


class GenerateCodeMixin:
    """
    Mixin для генерации кода подтверждения.
    """

    def _generate_code(self, length: int = 4) -> str:
        """
        Генерирует случайный числовой код заданной длины.

        :param length: Длина генерируемого кода.
        :type length: int
        :return: Сгенерированный код.
        :rtype: str
        """
        from string import digits
        from random import choices

        return "".join(choices(digits, k=length))


class SendVerifyEmailMixin(GenerateCodeMixin):
    """
    Mixin для отправки email с кодом подтверждения.
    Использует кэш для хранения сгенерированных кодов и временных ограничений.
    """

    _EMAIL_CACHE_LIFE_TIME: int = getattr(settings, "EMAIL_CACHE_LIFE_TIME", 60 * 60)
    _EMAIL_CACHE_REMAINING_TIME: int = getattr(
        settings, "EMAIL_CACHE_REMAINING_TIME", 60 * 2
    )

    def _get_code_cache_key(self, salt: str) -> str:
        """
        Генерирует ключ для кэша на основе переданного значения.

        :param salt: Уникальная строка (например, email).
        :type salt: str
        :return: Ключ для кэша.
        :rtype: str
        """
        return f"CODE_CACHE_{salt}"

    def _get_code(self, email: str) -> Optional[dict]:
        """
        Получает данные кода из кэша.

        :param email: Адрес email для поиска кода.
        :type email: str
        :return: Данные из кэша или None, если кода нет.
        :rtype: Optional[dict]
        """
        return cache.get(key=self._get_code_cache_key(email))

    def _invalidate_cache(self, email: str) -> None:
        """
        Удаляет данные кода из кэша.

        :param email: Адрес email для удаления данных из кэша.
        :type email: str
        """
        cache.delete(self._get_code_cache_key(email))

    def _get_expiration_time(self) -> float:
        """
        Вычисляет время истечения кода подтверждения.

        :return: Время истечения в секундах.
        :rtype: float
        """
        return time.time() + self._EMAIL_CACHE_REMAINING_TIME

    def _set_cache(self, cache_key: str, code: str) -> float:
        """
        Устанавливает данные кода в кэш.

        :param cache_key: Ключ для кэша.
        :type cache_key: str
        :param code: Код подтверждения.
        :type code: str
        :return: Время истечения кэша.
        :rtype: float
        """
        et = self._get_expiration_time()
        cache.set(
            key=cache_key,
            value={
                "expiration_time": et,
                "code": code,
            },
            timeout=self._EMAIL_CACHE_LIFE_TIME,
        )
        return et

    def _get_context(
        self,
        request,
        user,
        email: str,
        code: Optional[str] = None,
    ) -> dict:
        """
        Создает контекст для email сообщения.

        :param request: Объект HTTP-запроса.
        :param user: Пользователь.
        :param email: Адрес email.
        :param code: Код подтверждения (если не указан, генерируется новый).
        :type code: Optional[str]
        :return: Контекст для email сообщения.
        :rtype: dict
        """
        if not code:
            code = self._generate_code()

        domain = get_base_domain()

        context = {
            "code": code,
            "email": email,
            "domain": domain,
            "site_name": domain,
            "protocol": ["https", "http"][settings.DEBUG],
            "name": (
                f"{user.first_name} {user.last_name}"
                if user.is_authenticated and any([user.first_name, user.last_name])
                else "уважаемый клиент"
            ),
        }
        return context

    def _send_confirm_email(
        self,
        request,
        user,
        email: str,
        code: Optional[str] = None,
        topik: Optional[str] = None,
        cache_key: Optional[str] = None,
        set_cache: bool = True,
        email_template_name: str = "email/register_code.html",
    ) -> Response:
        """
        Отправляет email с кодом подтверждения.

        :param request: Объект HTTP-запроса.
        :param user: Пользователь.
        :param email: Адрес email.
        :param code: Код подтверждения (если не указан, генерируется новый).
        :param topik: Тема письма.
        :param cache_key: Ключ для кэша.
        :param set_cache: Флаг для установки кода в кэш.
        :param email_template_name: Имя шаблона email.
        :return: Ответ с результатом отправки.
        :rtype: Response
        """
        if not cache_key:
            cache_key = self._get_code_cache_key(email)

        if not code:
            code = self._generate_code(length=settings.REGISTER_CODE_LENGTH)

        if not topik:
            topik = _(f"Подтверждение почты {get_base_domain()}")

        cached_data = cache.get(cache_key)
        if cached_data:
            expiration_time = cached_data.get("expiration_time")
            remaining_time = expiration_time - time.time()
            if remaining_time >= 0:
                return Response(
                    {
                        "message": f"Please wait. Time remaining: {int(remaining_time) // 60:02d}:{int(remaining_time) % 60:02d}",
                        "expiration_time": expiration_time,
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

        context = self._get_context(request, user, email, code)

        if set_cache:
            et = self._set_cache(cache_key, code)
        else:
            et = self._get_expiration_time()

        logo = getattr(settings, "LOGO_URL", None)
        attach_data = EmailService.get_attach_data(logo, "Content-ID", "<logo>")
        message = EmailService.build_message(email, topik, email_template_name, context)
        if attach_data is not None:
            message.attach(attach_data)

        result = EmailService.send(message, fail_silently=True)

        if result:
            return Response(
                {"message": "Message sent successfully", "expiration_time": et},
                status=HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Message sent failed"}, status=HTTP_400_BAD_REQUEST
            )
