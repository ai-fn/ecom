from rest_framework import test
from shop.models import Product, Category, Brand
from django.utils.text import slugify
from django.urls import reverse
# Create your tests here.

class TestProductModel(test.APITestCase):
    
    def setUp(self):
        self.brand = Brand.objects.create(name="dummy brand")
        self.category = Category.objects.create(name="dummy category")
        self.prod = Product.objects.create(title="dummy-product", category=self.category, brand=self.brand)
        self.prod1 = Product.objects.create(title="dummy-product1", category=self.category, brand=self.brand)

    def test_set_slug_on_prod_updates(self):
        self.prod2 = Product.objects.create(title="dummy-product2", category=self.category, brand=self.brand)
        self.prod3 = Product.objects.create(title="dummy-product3", category=self.category, brand=self.brand)
        self.assertEqual(self.prod3.slug, slugify(self.prod3.title) + f"-{self.prod3.id}")
    
    def test_respose_should_return_correct_value_of_similar_prods(self):
        path = reverse('api:shop:similar_products', args=[self.prod.pk])

        queryset = Product.objects.exclude(pk=self.prod.pk)
        self.prod.similar_products.add(*queryset.values_list('pk', flat=True))
        response = self.client.get(path).json()
        similar_prods = response.get('similar_products')
        print(len(similar_prods), len(queryset))
        self.assertEqual(len(similar_prods), len(queryset))
