import unittest

from django.urls import reverse

from rest_framework_simplejwt.settings import api_settings
from rest_framework import status, test

from account.models import CustomUser
from shop.models import Category, Brand
from cart.models import Product, CartItem, Order, ProductsInOrder

# Create your tests here.


class OrderViewSetTests(test.APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(
            email="dummy@gmail.com", password="dummy", username="dummy-users"
        )
        self.category = Category.objects.create(name="dummy category")
        self.brand = Brand.objects.create(name="dummy brand")
        self.prod1 = Product.objects.create(
            category=self.category,
            brand=self.brand,
            title="dummy title",
            description="dummy description",
            slug="dummy-slug1",
        )
        self.prod2 = Product.objects.create(
            category=self.category,
            brand=self.brand,
            title="dummy title",
            description="dummy description",
            slug="dummy-slug2",
        )
        self.cart_item = CartItem.objects.create(
            customer=self.user, quantity=1, product_id=self.prod1.id
        )

    def test_create_order_from_cart(self):
        url = "/api/cart/orders/"

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data={"address": "г. Воронеж, ул. Донбасская, 16е"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(ProductsInOrder.objects.count(), 1)
        self.assertEqual(CartItem.objects.filter(customer=self.user).count(), 0)


if __name__ == "__main__":
    unittest.main()
