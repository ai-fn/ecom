import unittest
from rest_framework import test
from shop.models import Product, Category, Brand
from django.urls import reverse


class TestProductModel(test.APITestCase):

    def setUp(self):
        self.brand = Brand.objects.create(name="dummy brand", order=1)
        self.category = Category.objects.create(name="dummy category", order=1)
        self.prod = Product.objects.create(
            title="dummy-product",
            category=self.category,
            article="dummy-article",
            brand=self.brand,
            slug="dummy-product",
        )
        self.prod1 = Product.objects.create(
            title="dummy-product1",
            category=self.category,
            article="dummy-article1",
            brand=self.brand,
            slug="dummy-product1",
        )

    def test_respose_should_return_correct_value_of_similar_prods(self):
        path = reverse("api:shop:similar_products", args=[self.prod.pk])

        queryset = Product.objects.exclude(pk=self.prod.pk)
        self.prod.similar_products.add(*queryset.values_list("pk", flat=True))
        response = self.client.get(path).json()
        similar_prods = response.get("results", set())

        self.assertEqual(len(similar_prods), len(self.prod.similar_products.all()))


if __name__ == "__main__":
    unittest.main()
