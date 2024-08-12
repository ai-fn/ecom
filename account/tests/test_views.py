from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.test import override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache


from account.views import AccountInfoViewSet

User = get_user_model()


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
class AccountInfoViewSetTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@example.com',
            phone='+71234567890'
        )
        self.new_email = 'newemail@example.com'
        self.token = RefreshToken.for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token.access_token))
        self.client.force_authenticate(user=self.user)
        self.viewset = AccountInfoViewSet()

    def test_retrieve_user_info(self):
        url = reverse('account:account-retrieve')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['phone'], self.user.phone)

    
    def test_partial_update_user_email(self):
        url = reverse('account:account-patch')
        response = self.client.patch(url, {'email': self.new_email})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.new_email)
        self.assertFalse(self.user.email_confirmed)

    def test_verify_email(self):
        with self.settings(CACHES={
            'default': {
                "BACKEND": "django.core.cache.backends.dummy.DummyCache"
            }
        }):
            self.test_partial_update_user_email()

        url = reverse('account:account-post')
        code = self.viewset._get_code(self.new_email)
        self.assertIsNotNone(code)

        response = self.client.post(url, {'code': code.get("code")})
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_confirmed)

    def test_resend_verify_email(self):
        url = reverse('account:account-post_resend')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['message'], "Message sent successfully")

        cached_data = self.viewset._get_code(self.user.email)
        self.assertIsNotNone(cached_data)
        self.assertIn("expiration_time", cached_data)
        self.assertIn("code", cached_data)

    def test_partial_update_existing_confirmed_email(self):
        url = reverse('account:account-patch')
        self.user.email_confirmed = True
        self.user.save()
        response = self.client.patch(url, {'email': self.user.email})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["email"][0]), 'Provided email already confirmed')

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_verify_email_with_invalid_code(self):
        self.test_partial_update_user_email()
        url = reverse('account:account-post')
        code = 'invalid'

        response = self.client.post(url, {'code': code})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_confirmed)

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_resend_verify_email_without_email(self):
        self.user.email = ""
        self.user.save()

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "")

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

        url = reverse('account:account-post_resend')
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'email is required')
