import time
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK


class GenerateCodeMixin:

    def _generate_code(self, length=4):
        from string import digits
        from random import choices

        return "".join(choices(digits, k=length))


class SendVerifyEmailMixin(GenerateCodeMixin):

    _EMAIL_CACHE_LIFE_TIME = getattr(settings, "EMAIL_CACHE_LIFE_TIME", 60 * 60)
    _EMAIL_CACHE_REMAINING_TIME = getattr(settings, "EMAIL_CACHE_REMAINING_TIME", 60 * 2)

    def _get_code_cache_key(self, salt: str):
        return f"CODE_CACHE_{salt}"

    def _get_code(self, email: str):
        return cache.get(key=self._get_code_cache_key(email))

    def _invalidate_cache(self, email: str) -> None:
        cache.delete(self._get_code_cache_key(email))

    def _generate_message(
        self,
        user,
        email,
        code: str = None,
    ):
        if not code:
            code = self._generate_code()

        domain = getattr(settings, "BASE_DOMAIN")
        context = {
            "email": email,
            "domain": domain,
            "site_name": domain,
            "user": user,
            "code": code,
            "protocol": ["https", "http"][settings.DEBUG],
        }
        return context

    def _send_confirm_email(
        self, request, user, email, email_template_name="email/register_code.html", cache_key: str = None, set_cache: bool = True, code: str = None,
    ):
        if not cache_key:
            cache_key = self._get_code_cache_key(email)
        if not code:
            code = self._generate_code(length=settings.REGISTER_CODE_LENGTH)

        cached_data = cache.get(cache_key)
        if cached_data:
            expiration_time = cached_data.get("expiration_time")
            remaining_time = expiration_time - time.time()
            if remaining_time >= 0:
                return Response(
                        {
                            "message": f"Please wait. Time remaining: {int(remaining_time) // 60:02d}:{int(remaining_time) % 60:02d}",
                            "expiration_time": expiration_time
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )

        context = self._generate_message(user, email, code)

        if set_cache:
            et = self._set_cache(cache_key, code)
        else:
            et = self._get_expiration_time()

        body = render_to_string(email_template_name, context)

        result = send_mail(
            _("Confrim email"),
            "",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True,
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD,
            html_message=body,
        )

        if result:
            return Response(
                {"message": "Message sent successfully", "expiration_time": et}, status=HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Message sent failed"}, status=HTTP_400_BAD_REQUEST
            )
    
    def _set_cache(self, cache_key: str, code: str):
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

    def _get_expiration_time(self):
        return time.time() + self._EMAIL_CACHE_REMAINING_TIME
