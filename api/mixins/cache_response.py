from typing import Any
from django.conf import settings
from django.core.cache import caches
from rest_framework.response import Response

cache = caches["dev_env"] if settings.DEBUG else caches["default"]


class CacheResponse:
    """
    Миксин для кэширования ответов представлений.

    Кэширует ответы методов `list` и `retrieve` с заданным временем жизни.
    """

    _list_cache_lifetime: int = 60 * 15
    _retrieve_cache_lifetime: int = 60 * 30

    def _generate_cache_key(self) -> str:
        """
        Генерирует ключ для кэширования на основе полного пути запроса.

        :return: Сгенерированный ключ для кэша.
        :rtype: str
        """
        return f"cache_response_{self.request.get_full_path()}"

    def _get_cached_response(
        self, view_method_name: str, cache_lifetime: int, *args: Any, **kwargs: Any
    ) -> Response:
        """
        Получение ответа из кэша или выполнение представления и кэширование ответа.

        :param view_method_name: Имя метода представления (`list` или `retrieve`).
        :type view_method_name: str
        :param cache_lifetime: Время жизни кэша в секундах.
        :type cache_lifetime: int
        :param args: Дополнительные позиционные аргументы.
        :param kwargs: Дополнительные именованные аргументы.
        :return: Ответ представления.
        :rtype: Response
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

    def list(self, request, *args: Any, **kwargs: Any) -> Response:
        """
        Возвращает кэшированный ответ для метода `list`.

        :param request: HTTP-запрос.
        :type request: HttpRequest
        :param args: Дополнительные позиционные аргументы.
        :param kwargs: Дополнительные именованные аргументы.
        :return: Кэшированный ответ.
        :rtype: Response
        """
        return self._get_cached_response(
            "list", self._list_cache_lifetime, *args, **kwargs
        )

    def retrieve(self, request, *args: Any, **kwargs: Any) -> Response:
        """
        Возвращает кэшированный ответ для метода `retrieve`.

        :param request: HTTP-запрос.
        :type request: HttpRequest
        :param args: Дополнительные позиционные аргументы.
        :param kwargs: Дополнительные именованные аргументы.
        :return: Кэшированный ответ.
        :rtype: Response
        """
        return self._get_cached_response(
            "retrieve", self._list_cache_lifetime, *args, **kwargs
        )
