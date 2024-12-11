from django.test import TestCase
from django.conf import settings
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from account.actions import SendCodeToTelegramAction


class SendCodeToTelegramActionTestCase(TestCase):
    def setUp(self):
        self.action = SendCodeToTelegramAction()
        self.action.message = "Ваш код: {code}. Никому не сообщайте его!"
        self.code = "123456"
        self.cache_key = "test_cache_key"

        settings.TG_BOT_TOKEN = "test_bot_token"
        settings.CHAT_ID = "test_chat_id"
        self.action.bot_token = settings.TG_BOT_TOKEN
        self.action.chat_id = settings.CHAT_ID
        self.action.link = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"

    @patch("requests.post")
    def test_send_message_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response

        result = self.action._send_message(
            request=None,
            code=self.code,
            cache_key=self.cache_key,
        )
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            self.action.link,
            params={
                "chat_id": self.action.chat_id,
                "text": self.action.message.format(code=self.code),
                "json": 1,
            },
        )

        cached_data = cache.get(self.cache_key)
        self.assertIsNotNone(cached_data)
        self.assertIn("expiration_time", cached_data)
        self.assertEqual(cached_data["code"], self.code)

    @patch("requests.post")
    def test_send_message_failure(self, mock_post):
        cache.clear()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": False,
            "error_code": 400,
            "description": "Bad Request",
        }
        mock_post.return_value = mock_response

        result = self.action._send_message(
            request=None,
            code=self.code,
            cache_key=self.cache_key,
        )
        self.assertFalse(result)
        mock_post.assert_called_once_with(
            self.action.link,
            params={
                "chat_id": self.action.chat_id,
                "text": self.action.message.format(code=self.code),
                "json": 1,
            },
        )

        cached_data = cache.get(self.cache_key)
        self.assertIsNone(cached_data)

    @patch("requests.post")
    def test_send_message_invalid_response_format(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        result = self.action._send_message(
            request=None,
            code=self.code,
            cache_key=self.cache_key,
        )
        self.assertFalse(result)
        mock_post.assert_called_once_with(
            self.action.link,
            params={
                "chat_id": self.action.chat_id,
                "text": self.action.message.format(code=self.code),
                "json": 1,
            },
        )

        cached_data = cache.get(self.cache_key)
        self.assertIsNone(cached_data)
