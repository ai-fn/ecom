from django.test import TestCase
from account.models import City, CityGroup, CustomUser


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
        self.city1 = City.objects.create(name="Москва")
        self.city2 = City.objects.create(name="Санкт-Петербург")
        
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
        self.city_group.cities.all().delete()
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

