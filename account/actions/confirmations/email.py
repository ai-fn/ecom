from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from api.mixins import SendVerifyEmailMixin
from api.serializers import EmailSerializer
from account.actions import SendCodeBaseAction
from shop.utils import get_base_domain


class SendCodeToEmailAction(SendCodeBaseAction, SendVerifyEmailMixin):
    lookup_field = "email"
    serializer_class = EmailSerializer

    def _send_message(self, request, code: str, cache_key: str) -> bool:
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
        user, message = super().verify(code, cache_salt)
        if user and not getattr(user, "email_confirmed"):
            user.email_confirmed = True
            user.save()

        return user, message
