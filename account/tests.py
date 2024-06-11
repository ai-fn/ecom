from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

from account.models import City, CityGroup, CustomUser

from account.views import AccountInfoViewSet

User = get_user_model()

class TestCitySignals(TestCase):
    def setUp(self):
        self.city = City.objects.create(name='Москва')

    def test_cases_are_set_correctly(self):
        self.city.name = 'Москва'
        self.city.save()

        self.assertEqual(self.city.nominative_case, 'Москва')
        self.assertEqual(self.city.genitive_case, 'Москвы')
        self.assertEqual(self.city.dative_case, 'Москве')
        self.assertEqual(self.city.accusative_case, 'Москву')
        self.assertEqual(self.city.instrumental_case, 'Москвой')
        self.assertEqual(self.city.prepositional_case, 'Москве')

    def test_cases_with_different_city(self):
        city2 = City.objects.create(name='Санкт-Петербург')
        
        self.assertEqual(city2.nominative_case, 'Санкт-Петербург')
        self.assertEqual(city2.genitive_case, 'Санкт-Петербурга')
        self.assertEqual(city2.dative_case, 'Санкт-Петербургу')
        self.assertEqual(city2.accusative_case, 'Санкт-Петербург')
        self.assertEqual(city2.instrumental_case, 'Санкт-Петербургом')
        self.assertEqual(city2.prepositional_case, 'Санкт-Петербурге')

    def tearDown(self):
        City.objects.all().delete()


class CityModelTest(TestCase):

    def setUp(self):
        self.city = City.objects.create(name="Москва")

    def test_cases_are_set_correctly(self):
        city = City.objects.get(name="Москва")
        self.assertEqual(city.nominative_case, "Москва")
        self.assertEqual(city.genitive_case, "Москвы")
        self.assertEqual(city.dative_case, "Москве")
        self.assertEqual(city.accusative_case, "Москву")
        self.assertEqual(city.instrumental_case, "Москвой")
        self.assertEqual(city.prepositional_case, "Москве")

    def test_cases_with_different_city(self):
        city2 = City.objects.create(name='Санкт-Петербург')
        self.assertEqual(city2.nominative_case, 'Санкт-Петербург')
        self.assertEqual(city2.genitive_case, 'Санкт-Петербурга')
        self.assertEqual(city2.dative_case, 'Санкт-Петербургу')
        self.assertEqual(city2.accusative_case, 'Санкт-Петербург')
        self.assertEqual(city2.instrumental_case, 'Санкт-Петербургом')
        self.assertEqual(city2.prepositional_case, 'Санкт-Петербурге')

    def test_signal_set_cases_on_create(self):
        self.assertEqual(self.city.nominative_case, "Москва")
        self.assertEqual(self.city.genitive_case, "Москвы")
        self.assertEqual(self.city.dative_case, "Москве")
        self.assertEqual(self.city.accusative_case, "Москву")
        self.assertEqual(self.city.instrumental_case, "Москвой")
        self.assertEqual(self.city.prepositional_case, "Москве")

    def test_signal_set_cases_on_update(self):
        self.city.name = "Новосибирск"
        self.city.save()
        self.city.refresh_from_db()
        self.assertEqual(self.city.nominative_case, "Новосибирск")
        self.assertEqual(self.city.genitive_case, "Новосибирска")
        self.assertEqual(self.city.dative_case, "Новосибирску")
        self.assertEqual(self.city.accusative_case, "Новосибирск")
        self.assertEqual(self.city.instrumental_case, "Новосибирском")
        self.assertEqual(self.city.prepositional_case, "Новосибирске")


class CityGroupModelTest(TestCase):

    def setUp(self):
        # Создаем города для тестов
        self.city1 = City.objects.create(name="Москва")
        self.city2 = City.objects.create(name="Санкт-Петербург")
        
        # Создаем группу городов
        self.city_group = CityGroup.objects.create(name="Основные города", main_city=self.city1)
        self.city_group.cities.add(self.city1, self.city2)

    def test_citygroup_creation(self):
        city_group = CityGroup.objects.get(name="Основные города")
        self.assertEqual(city_group.name, "Основные города")
        self.assertEqual(city_group.main_city, self.city1)
        self.assertIn(self.city1, city_group.cities.all())
        self.assertIn(self.city2, city_group.cities.all())

    def test_citygroup_update(self):
        self.city_group.name = "Измененная группа"
        self.city_group.save()
        self.assertEqual(self.city_group.name, "Измененная группа")

    def test_citygroup_deletion(self):
        city_group_id = self.city_group.id
        self.city_group.delete()
        with self.assertRaises(CityGroup.DoesNotExist):
            CityGroup.objects.get(id=city_group_id)

    def test_citygroup_str(self):
        self.assertEqual(str(self.city_group), "Группа Основные города")

    def test_citygroup_indexes(self):
        indexes = [index.name for index in CityGroup._meta.indexes]
        self.assertIn("citygroup_name_idx", indexes)
        self.assertIn("citygroup_main_city_idx", indexes)

    def test_citygroup_main_city_null(self):
        self.city_group.main_city = None
        self.city_group.save()
        self.assertIsNone(self.city_group.main_city)

    def test_citygroup_many_to_many(self):
        self.assertEqual(self.city_group.cities.count(), 2)
        self.city_group.cities.remove(self.city1)
        self.assertEqual(self.city_group.cities.count(), 1)
        self.assertNotIn(self.city1, self.city_group.cities.all())


class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            phone="+71234567890",
            first_name="Иван",
            last_name="Иванов",
            email="testuser@example.com"
        )

    def test_user_creation(self):
        user = CustomUser.objects.get(username="testuser")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.phone, "+71234567890")
        self.assertEqual(user.first_name, "Иван")
        self.assertEqual(user.last_name, "Иванов")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertFalse(user.is_customer)
        self.assertFalse(user.email_confirmed)
        self.assertIsNone(user.middle_name)
        self.assertIsNone(user.address)

    def test_user_update(self):
        self.user.first_name = "Петр"
        self.user.save()
        self.assertEqual(self.user.first_name, "Петр")

    def test_user_soft_delete(self):
        self.user.delete()
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_user_str(self):
        self.assertEqual(str(self.user), "CustomUser(+71234567890)")

    def test_user_indexes(self):
        indexes = [index.name for index in CustomUser._meta.indexes]
        self.assertIn("customuser_phone_idx", indexes)
        self.assertIn("customuser_address_idx", indexes)

    def test_create_user_with_no_phone(self):
        user = CustomUser.objects.create_user(
            username="testuser2",
            password="testpass123",
            email="testuser2@example.com"
        )
        self.assertIsNone(user.phone)
        self.assertEqual(user.email, "testuser2@example.com")

    def test_create_user_with_phone(self):
        user = CustomUser.objects.create_user(
            username="testuser3",
            password="testpass123",
            phone="+79876543210"
        )
        self.assertEqual(user.phone, "+79876543210")

    def test_create_user_with_full_data(self):
        user = CustomUser.objects.create_user(
            username="testuser4",
            password="testpass123",
            phone="+79876543210",
            first_name="Сергей",
            last_name="Петров",
            email="testuser4@example.com",
            address="ул. Ленина, д. 1",
            is_customer=True,
            email_confirmed=True,
            middle_name="Иванович"
        )
        self.assertEqual(user.phone, "+79876543210")
        self.assertEqual(user.first_name, "Сергей")
        self.assertEqual(user.last_name, "Петров")
        self.assertEqual(user.email, "testuser4@example.com")
        self.assertEqual(user.address, "ул. Ленина, д. 1")
        self.assertTrue(user.is_customer)
        self.assertTrue(user.email_confirmed)
        self.assertEqual(user.middle_name, "Иванович")


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
        print(response.json())
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
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data['message'], 'provided email address already confirmed')

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
