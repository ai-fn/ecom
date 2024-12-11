import time
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from rest_framework import status
from account.actions import SendCodeBaseAction


class SendCodeBaseActionTestCase(TestCase):
    def setUp(self):
        self.action = SendCodeBaseAction()
        self.factory = RequestFactory()
        self.lookup_field = "phone"
        self.salt = "+79943741239"

        self.req_data = {self.lookup_field: self.salt}

    def test_is_code_valid_success(self):
        salt = "test_salt"
        code = "123456"
        cache.set(self.action._get_code_cache_key(salt), {"code": code}, timeout=30)
        
        is_valid, message = self.action._is_code_valid(code, salt)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid code")

    @patch("django.core.cache.cache.get")
    def test_is_code_valid_failure_invalid_code(self, mock_cache_get):
        mock_cache_get.return_value = {
            "code": "1234",
            "expiration_time": time.time() + 60 * 2,
            "lookup_field": "dummy_username"
        }
        salt = "test_salt"

        is_valid, message = self.action._is_code_valid("123456", salt)
        self.assertFalse(is_valid)
        self.assertEqual(message, "Invalid confirmation code")

    def test_is_code_valid_failure_no_cache(self):
        salt = "test_salt"
        is_valid, message = self.action._is_code_valid("123456", salt)
        self.assertFalse(is_valid)
        self.assertEqual(message, "No confirmation codes for you.")

    @patch("account.actions.SendCodeBaseAction._send_message", return_value=True)
    def test_execute_success(self, mock_send_message):
        request = self.factory.post(
            "/api/send-code/",
            data=self.req_data,
            content_type="application/json",
        )
        response = self.action.execute(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("expiration_time", response.data)

    @patch("account.actions.SendCodeBaseAction._send_message", return_value=False)
    def test_execute_failure_send_message(self, mock_send_message):
        request = self.factory.post(
            "/api/send-code/",
            data=self.req_data,
            content_type="application/json",
        )
        response = self.action.execute(request)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Failed")

    @patch("django.core.cache.cache.get")
    def test_execute_conflict_on_retry(self, mock_cache_get):
        mock_cache_get.return_value = {
            "code": "1234",
            "expiration_time": time.time() + 60 * 2,
            "lookup_field": "dummy_username"
        }

        request = self.factory.post(
            "/api/send-code/",
            data=self.req_data,
            content_type="application/json",
        )
        response = self.action.execute(request)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("Time remaining", response.data["message"])
