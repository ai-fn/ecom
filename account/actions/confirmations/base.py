import time

from django.conf import settings
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from api.serializers.phone import PhoneSerializer
from api.mixins import GenerateCodeMixin


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

            return Response({"success": True, "expiration_time": et}, status=status.HTTP_200_OK)

        return Response({"error": "Failed"}, status=status.HTTP_400_BAD_REQUEST)

    def _set_cache(self, salt: str, code: str):
        et = time.time() + self.remaining_time
        cache.set(
            self._get_code_cache_key(salt),
            {
                "expiration_time": et,
                "code": code,
                self.lookup_field: self.kwargs[self.lookup_field]
            },
            timeout=self.code_lifetime,
        )
        print(cache.get(self._get_code_cache_key(salt)))
        return et

    def _invalidate_cache(self, salt):
        cache.delete(self._get_code_cache_key(salt))

    def _send_message(self, request, code: str, cache_key: str) -> bool:
        raise NotImplementedError("Method must be implemented!")
