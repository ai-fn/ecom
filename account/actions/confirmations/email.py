from api.mixins import SendVerifyEmailMixin
from account.actions import SendCodeBaseAction
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
from api.serializers import EmailSerializer


class SendCodeToEmailAction(SendCodeBaseAction, SendVerifyEmailMixin):
    lookup_field = "email"
    serializer_class = EmailSerializer

    def _send_message(self, request, code: str, cache_key: str) -> bool:
        email = self.kwargs[self.lookup_field]
        response = self._send_confirm_email(request, request.user, email, "email/login_code.html", cache_key=cache_key, set_cache=False, code=code)
        return 200 <= response.status_code < 400
