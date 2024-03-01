from rest_framework import test
from shop.models import Product, Category, Brand
from django.utils.text import slugify
# Create your tests here.

class TestProductModel(test.APITestCase):

    def test_set_slug_on_prod_updates(self):
        self.brand = Brand.objects.create(name="dummy brand")
        self.category = Category.objects.create(name="dummy category")
        self.prod = Product.objects.create(title="dummy-product", category=self.category, brand=self.brand)
        self.prod1 = Product.objects.create(title="dummy-product1", category=self.category, brand=self.brand)
        self.assertEqual(self.prod1.slug, slugify(self.prod1.title) + "-%s" % self.prod1.id)
