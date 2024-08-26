import unittest
from django.test import TestCase
from shop.models import Product, Category, Brand, City
from export_app.services import ExportService
import pandas as pd


class ExportServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category1 = Category.objects.create(name='Category 1', slug='cat1')
        cls.category2 = Category.objects.create(name='Category 2', slug='cat2')
        cls.category3 = Category.objects.create(name='Category 3', slug='cat3')

        cls.brand = Brand.objects.create(name='Brand 1')

        cls.city1 = City.objects.create(name='City 1')
        cls.city2 = City.objects.create(name='City 2')

        cls.product1 = Product.objects.create(
            category=cls.category1,
            h1_tag='Product 1',
            brand=cls.brand,
            title='Product 1 Title',
            description='Description 1',
            slug='product-1',
            in_stock=True,
            is_popular=True,
            is_new=True,
            priority=1,
            article='P1'
        )
        cls.product2 = Product.objects.create(
            category=cls.category2,
            h1_tag='Product 2',
            brand=cls.brand,
            title='Product 2 Title',
            description='Description 2',
            slug='product-2',
            in_stock=True,
            is_popular=False,
            is_new=False,
            priority=2,
            article='P2'
        )

        cls.product1.additional_categories.add(cls.category2, cls.category3)
        cls.product2.additional_categories.add(cls.category1)
        cls.product1.unavailable_in.add(cls.city1, cls.city2)
        cls.product2.unavailable_in.add(cls.city1)

        cls.product1.similar_products.add(cls.product2)
        cls.product2.similar_products.add(cls.product1)

    def test_prepare_data(self):
        fields = [
            'category', 'additional_categories', 'h1_tag', 'brand', 'title',
            'description', 'catalog_image', 'search_image', 'original_image',
            'slug', 'similar_products', 'in_stock', 'is_popular', 'is_new',
            'priority', 'frequenly_bought_together', 'article', 'unavailable_in'
        ]
        reg_fields, m2m_fields = ExportService.prepare_data(Product, fields)
        
        self.assertListEqual(reg_fields, [
            'category', 'h1_tag', 'brand', 'title', 'description', 'catalog_image',
            'search_image', 'original_image', 'slug', 'in_stock', 'is_popular',
            'is_new', 'priority', 'article'
        ])
        self.assertListEqual(m2m_fields, [
            'additional_categories', 'similar_products', 'frequenly_bought_together', 'unavailable_in'
        ])

    def test_create_dataframe_with_invalid_model(self):
        model_fields = {
            'product_invalid_name': ['name', 'description']
        }

        with self.assertRaises(ValueError) as context:
            ExportService.create_dataframe(model_fields)

        self.assertEqual(str(context.exception), 'Invalid model names (product_invalid_name)')

    def test_create_dataframe_with_no_m2m_fields(self):
        model_fields = {
            'product': ['title', 'description']
        }

        df = ExportService.create_dataframe(model_fields)
        
        expected_data = {
            'Товар_title': [self.product2.title, self.product1.title],
            'Товар_description': [self.product2.description, self.product1.description],
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(df, expected_df, check_like=True)
    
    def test_create_dataframe_with_no_reg_fields(self):
        model_fields = {
            'product': ['similar_products']
        }

        df = ExportService.create_dataframe(model_fields)
        
        expected_data = {
            'Товар_similar_products': [self.product1.pk, self.product2.pk]
        }
        expected_df = pd.DataFrame(expected_data)

        df = df.applymap(str)
        expected_df = expected_df.applymap(str)

        assert df.equals(expected_df), "DataFrames are not equal"

    def test_create_dataframe_with_empty_model_fields(self):
        model_fields = {
            'product': []
        }

        df = ExportService.create_dataframe(model_fields)
        
        expected_data = {}
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(df, expected_df)

    def test_create_dataframe(self):
        model_fields = {
            'product': [
                'category', 'additional_categories', 'h1_tag', 'brand', 'title',
                'description', 'slug', 'similar_products', 'in_stock', 'is_popular',
                'is_new', 'priority', 'article', 'unavailable_in'
            ]
        }
        df = ExportService.create_dataframe(model_fields)
        
        self.assertIsInstance(df, pd.DataFrame)
        
        expected_columns = [
            'Товар_category', 'Товар_additional_categories', 'Товар_h1_tag',
            'Товар_brand', 'Товар_title', 'Товар_description', 'Товар_slug',
            'Товар_similar_products', 'Товар_in_stock', 'Товар_is_popular',
            'Товар_is_new', 'Товар_priority', 'Товар_article', 'Товар_unavailable_in'
        ]
        
        self.assertTrue(set(expected_columns).issubset(set(df.columns)))
        self.assertEqual(len(df), 2)

        self.assertEqual(df.iloc[1]['Товар_category'], str(self.category1.pk))
        self.assertEqual(df.iloc[1]['Товар_h1_tag'], 'Product 1')
        self.assertEqual(df.iloc[1]['Товар_brand'], str(self.brand.pk))
        self.assertEqual(df.iloc[1]['Товар_title'], 'Product 1 Title')
        self.assertEqual(df.iloc[1]['Товар_description'], 'Description 1')
        self.assertEqual(df.iloc[1]['Товар_slug'], 'product-1')
        self.assertEqual(df.iloc[1]['Товар_similar_products'], str(self.product2.pk))
        self.assertEqual(df.iloc[1]['Товар_in_stock'], True)
        self.assertEqual(df.iloc[1]['Товар_is_popular'], True)
        self.assertEqual(df.iloc[1]['Товар_is_new'], True)
        self.assertEqual(df.iloc[1]['Товар_priority'], 1)
        self.assertEqual(df.iloc[1]['Товар_article'], 'P1')
        self.assertEqual(df.iloc[1]['Товар_additional_categories'], f"{self.category2.pk}, {self.category3.pk}")
        self.assertEqual(df.iloc[1]['Товар_unavailable_in'], f"{self.city1.pk}, {self.city2.pk}")

        self.assertEqual(df.iloc[0]['Товар_category'], str(self.category2.pk))
        self.assertEqual(df.iloc[0]['Товар_h1_tag'], 'Product 2')
        self.assertEqual(df.iloc[0]['Товар_brand'], str(self.brand.pk))
        self.assertEqual(df.iloc[0]['Товар_title'], 'Product 2 Title')
        self.assertEqual(df.iloc[0]['Товар_description'], 'Description 2')
        self.assertEqual(df.iloc[0]['Товар_slug'], 'product-2')
        self.assertEqual(df.iloc[0]['Товар_similar_products'], str(self.product1.pk))
        self.assertEqual(df.iloc[0]['Товар_in_stock'], True)
        self.assertEqual(df.iloc[0]['Товар_is_popular'], False)
        self.assertEqual(df.iloc[0]['Товар_is_new'], False)
        self.assertEqual(df.iloc[0]['Товар_priority'], 2)
        self.assertEqual(df.iloc[0]['Товар_article'], 'P2')
        self.assertEqual(df.iloc[0]['Товар_additional_categories'], f"{self.category1.pk}")
        self.assertEqual(df.iloc[0]['Товар_unavailable_in'], f"{self.city1.pk}")

if __name__ == '__main__':
    unittest.main()
