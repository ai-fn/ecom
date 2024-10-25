import time

from loguru import logger

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.db.utils import IntegrityError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError

from account.models import CustomUser
from api.mixins import GenerateCodeMixin
from api.serializers.phone import PhoneSerializer
from api.serializers.confirm_code import ConfirmCodeSerializer


class SendCodeBaseAction(GenerateCodeMixin):
    link: str = None
    api_key: str = None
    kwargs = dict()
    lookup_field: str = "phone"
    permission_classes = [AllowAny]
    serializer_class = PhoneSerializer
    message: str = "Ваш код: {code}. Никому не сообщайте его!"

    code_lifetime = int(getattr(settings, "CONFIRM_CODE_LIFE_TIME", 60 * 30))
    remaining_time = int(getattr(settings, "CONFIRM_CODE_REMAINING_TIME", 60 * 2))

    def _get_code_cache_key(self, salt: str) -> str:
        prefix = getattr(settings, "CONFIRM_CODE_PREFIX", "CONFIRM_CODE_PREFIX")
        return f"{prefix}_{salt}"

    def _invalidate_cache(self, salt):
        cache.delete(self._get_code_cache_key(salt))

    def _send_message(self, request, code: str, cache_key: str) -> bool:
        raise NotImplementedError("Method must be implemented!")

    def _is_code_valid(self, code: str, cache_salt: str):

        cached_key = self._get_code_cache_key(cache_salt)
        cached_data = cache.get(cached_key)
        if not cached_data:
            return False, "No confirmation codes for you."

        cached_code = cached_data.get("code")

        if code != cached_code:
            return False, "Invalid confirmation code"

        return True, "Valid code"

    def verify(self, code: str, cache_salt: str) -> AbstractUser | None:
        user = None
        is_valid, message = self._is_code_valid(code, cache_salt)
        if is_valid:
            cached_data = cache.get(self._get_code_cache_key(cache_salt))
            lookup_value = cached_data.get(self.lookup_field)
            fields = {self.lookup_field: lookup_value}

            q = Q(**fields)
            if self.lookup_field != "username":
                q |= Q(username=lookup_value)

            user = CustomUser.objects.filter(q).first()
            if not user:
                user = CustomUser.objects.create(**fields, is_active=True)
                user.set_password(lookup_value)
                user.save()
            
            if getattr(user, self.lookup_field, None) != lookup_value:
                try:
                    setattr(user, self.lookup_field, lookup_value)
                    user.save()
                except IntegrityError as err:
                    logger.error(f"Error on code confirmation: {str(err)}")
                    raise ValidationError(str(err))

        self._invalidate_cache(cache_salt)

        return user, message

    def execute(self, request):
        serializer_instance = self.serializer_class(data=request.data)
        if not serializer_instance.is_valid():
            return Response(
                serializer_instance.errors, status=status.HTTP_400_BAD_REQUEST
            )

        lookup_value: str = serializer_instance.data.get(self.lookup_field)
        self.kwargs[self.lookup_field] = lookup_value

        ip = request.META.get("REMOTE_ADDR", lookup_value)
        cache_key = self._get_code_cache_key(ip)
        cached_data = cache.get(cache_key)

        if cached_data:
            ren_time = cached_data.get("expiration_time") - time.time()
            if ren_time >= 0:
                return Response(
                    {
                        "message": f"Please wait. Time remaining: {int(ren_time) // 60:02d}:{int(ren_time) % 60:02d} seconds"
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        code = self._generate_code(length=settings.LOGIN_CODE_LENGTH)
        result = self._send_message(request, code, cache_key)
        if result:
            et = self._set_cache(ip, code)

            return Response(
                {"success": True, "expiration_time": et}, status=status.HTTP_200_OK
            )

        return Response({"error": "Failed"}, status=status.HTTP_400_BAD_REQUEST)

    def _set_cache(self, salt: str, code: str):
        et = time.time() + self.remaining_time
        cache.set(
            self._get_code_cache_key(salt),
            {
                "expiration_time": et,
                "code": code,
                self.lookup_field: self.kwargs[self.lookup_field],
            },
            timeout=self.code_lifetime,
        )
        return et
