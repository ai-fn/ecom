import os
import pandas as pd
from decimal import Decimal
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from shop.models import Product, CityGroup, Price, Category, Brand, City
from import_app.tasks import ImportTaskService

class ImportTaskServiceTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Создаем ContentType для Price
        cls.model_type = ContentType.objects.create(app_label='myapp', model='price')
        
        # Создаем связанные модели
        cls.category1 = Category.objects.create(name='Category 1', slug='category-1')
        cls.brand1 = Brand.objects.create(name='Brand 1', slug='brand-1')
        cls.city1 = City.objects.create(name='City 1', domain='city1.com')
        cls.city2 = City.objects.create(name='City 2', domain='city2.com')
        cls.city_group1 = CityGroup.objects.create(name='City Group 1', main_city=cls.city1)
        cls.city_group2 = CityGroup.objects.create(name='City Group 2', main_city=cls.city2)
        cls.product1 = Product.objects.create(
            category=cls.category1,
            title='Product 1',
            slug='product-1',
            article='P1',
            brand=cls.brand1,
        )
        cls.product2 = Product.objects.create(
            category=cls.category1,
            title='Product 2',
            slug='product-2',
            article='P2',
        )

        # Создаем тестовый Excel файл
        cls.test_file_path = '/tmp/test_price_import.xlsx'
        data = {
            'product_id': [cls.product1.id, cls.product2.id, cls.product1.id, cls.product2.id],
            'city_group_id': [cls.city_group1.id, cls.city_group1.id, cls.city_group2.id, cls.city_group2.id],
            'price': [100.00, 150.00, 200.00, 250.00],
            'old_price': [90.00, 140.00, 190.00, None]
        }
        df = pd.DataFrame(data)
        df.to_excel(cls.test_file_path, index=False)

    def test_process_dataframe(self):
        import_settings = {
            'path_to_images': '/tmp/import_images/',
            'fields': {
                'price': {
                    'product': 'product_id',
                    'city_group': 'city_group_id',
                    'price': 'price',
                    'old_price': 'old_price',
                }
            }
        }

        df = pd.read_excel(self.test_file_path)

        import_service = ImportTaskService()
        import_service.process_dataframe(df, import_settings=import_settings)
        
        self.assertEqual(Price.objects.count(), 4)
        price1 = Price.objects.get(product=self.product1, city_group=self.city_group1)
        self.assertEqual(price1.price, Decimal('100.00'))
        self.assertEqual(price1.old_price, Decimal('90.00'))
        
        price2 = Price.objects.get(product=self.product2, city_group=self.city_group1)
        self.assertEqual(price2.price, Decimal('150.00'))
        self.assertEqual(price2.old_price, Decimal('140.00'))
        
        price3 = Price.objects.get(product=self.product1, city_group=self.city_group2)
        self.assertEqual(price3.price, Decimal('200.00'))
        self.assertEqual(price3.old_price, Decimal('190.00'))
        
        price4 = Price.objects.get(product=self.product2, city_group=self.city_group2)
        self.assertEqual(price4.price, Decimal('250.00'))
        self.assertIsNone(price4.old_price)

    def test_categorize_fields(self):
        fields = {
            'product': 'product_id',
            'city_group': 'city_group_id',
            'price': 'price',
            'old_price': 'old_price',
        }

        model = Price
        import_service = ImportTaskService()
        foreign_key_fields, image_fields, decimal_fields, unique_fields = import_service.categorize_fields(model, fields)
        
        self.assertIn('product_id', foreign_key_fields.values())
        self.assertIn('city_group_id', foreign_key_fields.values())
        self.assertIn('price', decimal_fields.values())
        self.assertIn('old_price', decimal_fields.values())
        self.assertEqual(image_fields, dict())

    def test_prepare_data(self):
        row = {
            'product_id': self.product1.id,
            'city_group_id': self.city_group1.id,
            'price': 100.00,
            'old_price': 90.00
        }
        fields = {
            'product': 'product_id',
            'city_group': 'city_group_id',
            'price': 'price',
            'old_price': 'old_price',
        }
        foreign_key_fields = {'product': 'product_id', 'city_group': 'city_group_id'}
        image_fields = dict()
        decimal_fields = {'price': 'price', 'old_price': 'old_price'}
        path_to_images = '/tmp/import_images/'

        import_service = ImportTaskService()
        data = import_service.prepare_data(row, fields, image_fields, decimal_fields, foreign_key_fields, path_to_images)
        
        self.assertEqual(data['product'], self.product1.id)
        self.assertEqual(data['city_group'], self.city_group1.id)
        self.assertEqual(data['price'], Decimal('100.00'))
        self.assertEqual(data['old_price'], Decimal('90.00'))

    def test_update_or_create_instance(self):

        data = {
            'product': self.product1.id,
            'city_group': self.city_group1.id,
            'price': Decimal('110.00'),
            'old_price': Decimal('95.00')
        }
        unique_fields = {'product': 'product_id', 'city_group' : 'city_group_id'}

        import_service = ImportTaskService()
        import_service.update_or_create_instance(Price, data, unique_fields)
        
        self.assertEqual(Price.objects.count(), 1)
        price = Price.objects.get(product=self.product1, city_group=self.city_group1)
        self.assertEqual(price.price, Decimal('110.00'))
        self.assertEqual(price.old_price, Decimal('95.00'))
