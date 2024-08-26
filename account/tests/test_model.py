from django.test import TestCase
from account.models import City, CityGroup, CustomUser


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

