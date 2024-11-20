from django.test import TestCase
from api.test_utils import send_request
from shop.models import CustomUser
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class TokenTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_token_obtain_pair(self):
        response = send_request(self.client.post, 
            "/api/token/", {"username": "testuser", "password": "testpassword"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        response = send_request(self.client.post, "/api/token/refresh/", {"refresh": str(refresh)})

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_invalid_token_obtain_pair(self):
        response = send_request(self.client.post, 
            "/api/token/", {"username": "invaliduser", "password": "invalidpassword"}
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)
