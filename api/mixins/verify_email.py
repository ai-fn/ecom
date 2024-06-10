import time
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
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


class SendVirifyEmailMixin(GenerateCodeMixin):

    _EMAIL_CACHE_PREFIX = getattr(settings, "EMAIL_CACHE_PREFIX", "EMAIL_CACHE_PREFIX")
    _EMAIL_CACHE_LIFE_TIME = getattr(settings, "EMAIL_CACHE_LIFE_TIME", 60 * 60)
    _EMAIL_CACHE_REMAINING_TIME = getattr(settings, "EMAIL_CACHE_REMAINING_TIME", 60 * 2)


    def _get_code(self, email: str):
        return cache.get(key=self._get_cache_key(email))

    def _get_cache_key(self, email: str) -> str:
        return f"{self._EMAIL_CACHE_PREFIX}_{email}"

    def _invalidate_cache(self, email: str) -> None:
        cache.delete(self._get_cache_key(email))

    def _generate_message(
        self,
        request,
        user,
        email,
    ):
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        code = self._generate_code()
        expiration_time = time.time() + self._EMAIL_CACHE_REMAINING_TIME
        cache.set(
            key=self._get_cache_key(email),
            value={
                "expiration_time": expiration_time,
                "code": code,
            },
            timeout=self._EMAIL_CACHE_LIFE_TIME,
        )

        context = {
            "email": email,
            "domain": domain,
            "site_name": site_name,
            "user": user,
            "code": code,
            "protocol": ["https", "http"][settings.DEBUG],
        }
        return context, expiration_time

    def _send_confirm_email(
        self, request, user, email, email_template_name="email/index.html"
    ):
        cached_data = self._get_code(email)
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

        context, expiration_time = self._generate_message(request, user, email)
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
                {"message": "Message sent successfully", "expiration_time": expiration_time}, status=HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Message sent failed"}, status=HTTP_400_BAD_REQUEST
            )
