from django.test import TestCase
from account.models import City


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
