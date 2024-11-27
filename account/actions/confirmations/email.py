from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from api.mixins import SendVerifyEmailMixin
from api.serializers import EmailSerializer
from account.actions import SendCodeBaseAction
from shop.utils import get_base_domain


class SendCodeToEmailAction(SendCodeBaseAction, SendVerifyEmailMixin):
    """
    Класс для отправки кода подтверждения на email пользователя.

    Класс объединяет функциональность базового действия для отправки кода
    (`SendCodeBaseAction`) и функциональность проверки email (`SendVerifyEmailMixin`).
    """

    lookup_field = "email"
    serializer_class = EmailSerializer

    def _send_message(self, request, code: str, cache_key: str) -> bool:
        """
        Отправляет письмо с кодом подтверждения на указанный email.

        :param request: Объект HTTP-запроса, содержащий информацию о пользователе.
        :type request: HttpRequest
        :param code: Код подтверждения для отправки.
        :type code: str
        :param cache_key: Ключ для хранения данных в кэше.
        :type cache_key: str
        :return: Возвращает ``True``, если письмо отправлено успешно (HTTP-статус 200-399),
                 иначе ``False``.
        :rtype: bool
        """

        email = self.kwargs[self.lookup_field]
        response = self._send_confirm_email(
            request,
            request.user,
            email,
            code=code,
            set_cache=False,
            cache_key=cache_key,
            topik=_(f"Авторизация {get_base_domain()}"),
            email_template_name="email/login_code.html",
        )
        return 200 <= response.status_code < 400
    
    def verify(self, code: str, cache_salt: str) -> AbstractUser | None:
        """
        Проверяет код подтверждения и обновляет статус подтверждения email.

        :param code: Код подтверждения, введенный пользователем.
        :type code: str
        :param cache_salt: Соль для поиска записи в кэше.
        :type cache_salt: str
        :return: Возвращает пользователя, если код успешно подтвержден, иначе ``None``.
        :rtype: AbstractUser | None
        """

        user, message = super().verify(code, cache_salt)
        if user and not getattr(user, "email_confirmed"):
            user.email_confirmed = True
            user.save()

        return user, message
