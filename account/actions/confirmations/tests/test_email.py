import time
from rest_framework import status
from django.core.cache import cache
from account.models import CustomUser
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from account.actions import SendCodeToEmailAction


class SendCodeToEmailActionTestCase(TestCase):
    def setUp(self):
        self.action = SendCodeToEmailAction()
        self.factory = RequestFactory()
        self.email = "test@example.com"
        self.code = "123456"
        self.cache_key = "test_cache_key"
        self.user = CustomUser.objects.create_user(
            username="testuser", email=self.email
        )

    @patch("api.mixins.SendVerifyEmailMixin._send_confirm_email")
    def test_send_message_success(self, mock_send_confirm_email):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_send_confirm_email.return_value = mock_response

        request = self.factory.get("/api/send-code/")
        request.user = self.user
        result = self.action._send_message(
            request=request,
            code=self.code,
            cache_key=self.cache_key,
        )
        self.assertTrue(result)
        mock_send_confirm_email.assert_called_once()

    @patch("api.mixins.SendVerifyEmailMixin._send_confirm_email")
    def test_send_message_failure(self, mock_send_confirm_email):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_send_confirm_email.return_value = mock_response

        request = self.factory.get("/api/send-code/")
        request.user = self.user

        result = self.action._send_message(
            request=request,
            code=self.code,
            cache_key=self.cache_key,
        )
        self.assertFalse(result)
        mock_send_confirm_email.assert_called_once()

    def test_verify_success(self):
        # Set up cache for valid code
        cache.set(
            self.action._get_code_cache_key(self.cache_key),
            {"code": self.code, "email": self.email},
            timeout=60,
        )
        user, message = self.action.verify(self.code, self.cache_key)
        self.assertIsNotNone(user)
        self.assertTrue(user.email_confirmed)
        self.assertEqual(message, "Valid code")

    @patch("django.core.cache.cache.get")
    def test_verify_failure_invalid_code(self, mock_cache_get):

        mock_cache_get.return_value = {
            "code": self.code,
            "expiration_time": time.time() + 60 * 2,
            "email": self.email,
        }

        # Set up cache for valid code
        user, message = self.action.verify(f"{self.code}-invalid", self.cache_key)
        self.assertIsNone(user)
        self.assertEqual(message, "Invalid confirmation code")

    def test_verify_failure_no_cache(self):
        user, message = self.action.verify(self.code, self.cache_key)
        self.assertIsNone(user)
        self.assertEqual(message, "No confirmation codes for you.")

    def test_execute_with_valid_data(self):
        cache.clear()
        request = self.factory.post(
            "/api/send-code/",
            data={"email": self.email},
            content_type="application/json",
        )
        request.user = self.user
        response = self.action.execute(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("expiration_time", response.data)

    def test_execute_with_invalid_data(self):
        request = self.factory.post(
            "/api/send-code/",
            data={},
            content_type="application/json",
        )
        response = self.action.execute(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
