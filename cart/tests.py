import unittest

from django.urls import reverse

from rest_framework import test, status

from account.models import City, CustomUser
from shop.models import Category, Brand, Price
from cart.models import Order, Product, CartItem, ProductsInOrder

# Create your tests here.


class OrderViewSetTests(test.APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(
            email="dummy@gmail.com", password="dummy", username="dummy-users"
        )
        self.city = City.objects.create(name="Москва")
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
        self.prices = [Price.objects.create(price=100, product=prod, city=self.city) for prod in (self.prod1, self.prod2)]
        self.cart_item = CartItem.objects.create(
            customer=self.user, quantity=1, product_id=self.prod1.id
        )

    def test_create_order_from_cart(self):
        query_params = {"city_domain": "moskva"}
        url = reverse("api:cart:orders-list") + '?' + '&'.join([f"{key}={value}" for key, value in query_params.items()])

        self.client.force_authenticate(user=self.user)
        data = {
            'region': "Воронежская область",
            'district': "Лискинский район",
            'city_name': "Воронеж",
            'street': "улица Садовая",
            'house': "101Б",
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(ProductsInOrder.objects.count(), 1)
        self.assertEqual(CartItem.objects.filter(customer=self.user).count(), 0)


if __name__ == "__main__":
    unittest.main()
