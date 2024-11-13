import unittest
from unittest import mock

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from shop.models import Category, Brand, Price
from account.models import City, CityGroup, CustomUser

from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from cart.models import Order, Product, CartItem, ProductsInOrder

User = get_user_model()


class OrderViewSetTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(
            email="dummy@gmail.com", password="dummy", username="dummy-users"
        )
        self.city_group = CityGroup.objects.create(name="Москва")
        self.city = City.objects.create(name="Москва", domain="moskva.domain.com")
        self.city_group.cities.add(self.city)

        self.category = Category.objects.create(name="dummy category", order=1)
        self.brand = Brand.objects.create(name="dummy brand", order=1)
        self.prod1 = Product.objects.create(
            category=self.category,
            brand=self.brand,
            title="dummy title",
            description="dummy description",
            slug="dummy-slug1",
            article="2093802",
        )
        self.prod2 = Product.objects.create(
            category=self.category,
            brand=self.brand,
            title="dummy title",
            description="dummy description",
            slug="dummy-slug2",
            article="2093801",
        )
        self.prices = [
            Price.objects.create(price=100, product=prod, city_group=self.city_group)
            for prod in (self.prod1, self.prod2)
        ]
        self.cart_item = CartItem.objects.create(
            customer=self.user, quantity=1, product_id=self.prod1.id
        )
        self.order_data = {
            "delivery_type": "delivery",
            "receiver_first_name": "Иван",
            "receiver_last_name": "Петров",
            "receiver_phone": "+79996740923",
            "receiver_email": "example@mail.ru",
            "address": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, Россия",
        }

    def test_create_order(self):

        url = self.get_order_url("voronezh.domain.com")

        self.client.force_authenticate(user=self.user)
        data = {
            "delivery_type": "delivery",
            "receiver_first_name": "Иван",
            "receiver_last_name": "Петров",
            "receiver_phone": "+79996740923",
            "receiver_email": "example@mail.ru",
            "address": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, Россия",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = self.get_order_url(self.city.domain)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(ProductsInOrder.objects.count(), 1)
        self.assertEqual(CartItem.objects.filter(customer=self.user).count(), 0)

    def authenticate_user(self):
        self.client.force_authenticate(user=self.user)

    def get_order_url(self, city_domain):
        return reverse("api:cart:orders-list") + f"?city_domain={city_domain}"

    def test_order_creation_fails_due_to_missing_price(self):

        self.authenticate_user()
        url = self.get_order_url("voronezh.domain.com")

        response = self.client.post(url, self.order_data, format="json")

        self.assertIn("error", response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_creation_succeeds_for_valid_data(self):

        self.authenticate_user()
        url = self.get_order_url("moskva.domain.com")

        response = self.client.post(url, self.order_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(ProductsInOrder.objects.count(), 1)
        self.assertEqual(CartItem.objects.filter(customer=self.user).count(), 0)

        order = Order.objects.first()
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.delivery_type, self.order_data["delivery_type"])


class CartCountViewTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@example.com", password="userpassword", username="user"
        )
        self.category = Category.objects.create(name="dummy category", order=1)
        self.brand = Brand.objects.create(name="dummy brand", order=1)
        self.prod = Product.objects.create(
            category=self.category,
            brand=self.brand,
            title="dummy title",
            description="dummy description",
            slug="dummy-slug1",
            article="2093802",
        )
        self.prod_2 = Product.objects.create(
            category=self.category,
            brand=self.brand,
            title="dummy title 2",
            description="dummy description 2",
            slug="dummy-slug2",
            article="2093801",
        )

        self.cart_url = reverse("api:cart:cart-count")

        self.cart_items = [
            CartItem.objects.create(product=self.prod, customer=self.user, quantity=10),
            CartItem.objects.create(
                product=self.prod_2, customer=self.user, quantity=20
            ),
        ]

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_get_cart_count_authenticated(self):
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 30)

    def test_get_cart_count_unauthenticated(self):
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


if __name__ == "__main__":
    unittest.main()
