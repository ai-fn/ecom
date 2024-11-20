from api.models import ApiKey

from rest_framework import status

from django.conf import settings
from django.core.cache import cache
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _


class ApiKeyMiddleware:

    _CACHE_EXPIRATION_TIME = 60 * 15

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if not self._is_authenticable_path(request):
            return self.get_response(request)

        msg, valid = self._validate_request(request)
        if not valid:
            return JsonResponse({"detail": _(msg)}, status=status.HTTP_401_UNAUTHORIZED)

        return self.get_response(request)

    def _validate_request(self, request: HttpRequest) -> tuple[str, bool]:
        provided_key = request.headers.get("X-Api-Key")
        if not provided_key:
            return "Api ключ не предоставлен.", False

        cache_key = ApiKey.get_cache_key(provided_key)
        cached_result = cache.get(cache_key)
        if not cached_result:
            try:
                key = ApiKey.objects.get(key=provided_key)
            except ApiKey.DoesNotExist:
                key = None

            ip = request.META.get("REMOTE_ADDR")
            host = request.headers.get('Host')

            if key is None or not key.is_valid():
                result = "Api ключ не действителен.", False

            elif not key.is_ip_allowed(ip):
                result = f"Запрос с ip '{ip}' не разрешён.", False
            
            elif not key.is_host_allowed(host):
                result = f"Запрос с хоста '{host}' не разрешён.", False

            else:
                result = None, True

            cache.set(cache_key, result, timeout=self._CACHE_EXPIRATION_TIME)
            return result
        else:
            return cached_result
    
    def _is_authenticable_path(self, request: HttpRequest) -> bool:
        for path in settings.API_KEY_EXCLUDED_PATHS:
            if request.path.startswith(path):
                return False

        return True
