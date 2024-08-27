from django.conf import settings
from django.core.cache import caches
from rest_framework.response import Response


cache = caches["dev_env"] if settings.DEBUG else caches["default"]


class CacheResponse:

    _list_cache_lifetime = 60 * 15
    _retrieve_cache_lifetime = 60 * 30

    def _generate_cache_key(self):
        return f"cache_response_{self.request.get_full_path()}"

    def _get_cached_response(self, view_method_name, cache_lifetime, *args, **kwargs):
        """
        Получение ответа из кэша или выполнение представления и кэширование ответа.
        """

        cache_key = self._generate_cache_key()
        cached_data = cache.get(cache_key) or {}
        if not cached_data:
            view_method = getattr(super(), view_method_name)
            response = view_method(self.request, *args, **kwargs)
            cached_data["data"] = response.data
            cached_data["status_code"] = response.status_code
            cache.set(cache_key, cached_data, cache_lifetime)

        return Response(cached_data["data"], status=cached_data["status_code"])

    def list(self, request, *args, **kwargs) -> Response:
        return self._get_cached_response(
            "list", self._list_cache_lifetime, *args, **kwargs
        )

    def retrieve(self, request, *args, **kwargs) -> Response:
        return self._get_cached_response(
            "retrieve", self._list_cache_lifetime, *args, **kwargs
        )
