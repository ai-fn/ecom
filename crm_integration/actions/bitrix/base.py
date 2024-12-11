import aiohttp
from loguru import logger
from typing import Any, Dict
from crm_integration.actions import BaseAction


class BaseBitrixAction(BaseAction):

    async def get_response(self, url: str, params: dict = None) -> tuple[dict, int]:
        return await self._send_request(url, "get", params=params)

    async def post_response(self, url: str, data: dict = None, params: dict = None
    ) -> tuple[dict, int]:
        return await self._send_request(url, "post", params=params, json=data)

    async def _send_request(
        self,
        url: str,
        method: str,
        json: dict = None,
        params: dict = None,
        headers: dict = None,
    ) -> Dict[str, Any]:
        """Отправляет асинхронный HTTP запрос.

        Args:
            url: URL для отправки запроса.
            method: Метод HTTP (например, 'get', 'post').
            json: Данные в формате JSON для отправки.
            params: Параметры запроса.
            headers: Заголовки запроса.

        Returns:
            dict: Ответ от API.

        Raises:
            aiohttp.ContentTypeError: Если произошла ошибка при обработке ответа.
        """

        async with aiohttp.ClientSession() as session:
            func = getattr(session, method.lower())
            async with func(
                url, params=params, json=json, headers=headers
            ) as response:
                response: aiohttp.ClientResponse
                try:
                    response_data = await response.json()
                    return response_data, response.status
                except aiohttp.ContentTypeError as err:
                    logger.error(str(err))
                    raise err
