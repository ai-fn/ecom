from django.test import TestCase
from unittest.mock import patch, MagicMock
from account.actions import SendCodeToSmsAction


class SendCodeToSmsActionTestCase(TestCase):
    def setUp(self):
        self.action = SendCodeToSmsAction()
        self.action.kwargs = {"phone": "+1234567890"}
        self.action.message = "Ваш код: {code}. Никому не сообщайте его!"
        self.code = "123456"
    
    @patch("requests.get")
    def test_send_message_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "OK"}
        mock_get.return_value = mock_response

        result = self.action._send_message(
            request=None,
            code=self.code,
        )
        self.assertTrue(result)
        mock_get.assert_called_once_with(
            self.action.link,
            params={
                "api_id": self.action.api_key,
                "to": self.action.kwargs["phone"],
                "msg": self.action.message.format(code=self.code),
                "json": 1,
            },
        )
    
    @patch("requests.get")
    def test_send_message_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ERROR",
            "error_code": 101,
            "description": "Invalid API key",
        }
        mock_get.return_value = mock_response

        result = self.action._send_message(
            request=None,
            code=self.code,
        )
        self.assertFalse(result)
        mock_get.assert_called_once_with(
            self.action.link,
            params={
                "api_id": self.action.api_key,
                "to": self.action.kwargs["phone"],
                "msg": self.action.message.format(code=self.code),
                "json": 1,
            },
        )

    @patch("requests.get")
    def test_send_message_invalid_response_format(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = self.action._send_message(
            request=None,
            code=self.code,
        )
        self.assertFalse(result)
        mock_get.assert_called_once_with(
            self.action.link,
            params={
                "api_id": self.action.api_key,
                "to": self.action.kwargs["phone"],
                "msg": self.action.message.format(code=self.code),
                "json": 1,
            },
        )
