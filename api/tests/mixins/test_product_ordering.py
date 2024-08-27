from django.test import TestCase
from shop.models import Product, Review, Price, Category
from account.models import CityGroup, CustomUser, City
from api.mixins import ProductSorting


class ProductSortingTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="test-ctg"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            phone="+71234567890",
            first_name="Иван",
            last_name="Иванов",
            email="testuser@example.com"
        )
        self.city = City.get_default_city()
        self.city_group = CityGroup.get_default_city_group()
        self.products = [
            Product.objects.create(
                title="product1",
                slug="product1",
                article="product1",
                category=self.category,
                is_new=True,
                is_popular=False,
                priority=1
            ),
            Product.objects.create(
                title="product2",
                slug="product2",
                article="product2",
                category=self.category,
                is_new=False,
                is_popular=True,
                priority=2
            ),
            Product.objects.create(
                title="product3",
                slug="product3",
                article="product3",
                category=self.category,
                is_new=True,
                is_popular=True,
                priority=3
            ),
        ]
        self.price = Price.objects.create(
            product=self.products[0],
            price=150.00,
            city_group=self.city_group,
            old_price=149.99
        )
        self.price1 = Price.objects.create(
            product=self.products[1],
            price=130.00,
            city_group=self.city_group,
            old_price=120.00
        )
        self.price2 = Price.objects.create(
            product=self.products[2],
            price=200.00,
            city_group=self.city_group,
            old_price=290.99
        )
        self.review = Review.objects.create(
            product=self.products[0],
            rating=2,
            user=self.user,
        )
        self.review1 = Review.objects.create(
            product=self.products[1],
            rating=5,
            user=self.user,
        )
        self.review2 = Review.objects.create(
            product=self.products[2],
            rating=1,
            user=self.user,
        )
        self.sorting = ProductSorting()

    def test_sort_by_price_with_city_domain(self):
        self.sorting.request = type('Request', (object,), {'query_params': {'order_by': 'price', 'city_domain': self.city.domain}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products[0].slug, "product2")
        self.assertEqual(sorted_products[1].slug, "product1")
        self.assertEqual(sorted_products[2].slug, "product3")
        self.assertEqual(len(sorted_products), Product.objects.count())

    def test_sort_by_price_without_city_domain(self):
        self.sorting.request = type('Request', (object,), {'query_params': {'order_by': 'price'}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products, list(Product.objects.all()))

    def test_sort_by_rating(self):
        self.sorting.request = type('Request', (object,), {'query_params': {'order_by': 'rating'}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products[0].slug, "product3")
        self.assertEqual(sorted_products[1].slug, "product1")
        self.assertEqual(sorted_products[2].slug, "product2")
        self.assertEqual(len(sorted_products), Product.objects.count())

    def test_sort_by_in_promo_with_city_domain(self):
        self.sorting.request = type('Request', (object,), {'query_params': {'order_by': '-in_promo', 'city_domain': self.city.domain}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products[0].slug, "product3")
        self.assertEqual(sorted_products[1].slug, "product1")
        self.assertEqual(sorted_products[2].slug, "product2")
        self.assertEqual(len(sorted_products), Product.objects.count())

    def test_sort_by_in_promo_without_city_domain(self):
        self.sorting.request = type('Request', (object,), {'query_params': {'order_by': '-in_promo'}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products, list(Product.objects.all()))

    def test_sort_by_recommend(self):
        self.sorting.request = type('Request', (object,), {'query_params': {'order_by': 'recommend'}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products[0].slug, "product3")
        self.assertEqual(sorted_products[1].slug, "product2")
        self.assertEqual(sorted_products[2].slug, "product1")
        self.assertEqual(len(sorted_products), Product.objects.count())

    def test_sort_by_invalid_field(self):
        self.sorting.request = type('Request', (object,), {'query_params': {'order_by': 'invalid_field'}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products, list(Product.objects.all()))
        self.assertEqual(len(sorted_products), Product.objects.count())

    def test_sort_without_ordering(self):
        self.sorting.request = type('Request', (object,), {'query_params': {}})
        sorted_queryset = self.sorting.sorted_queryset(Product.objects.all())
        sorted_products = list(sorted_queryset)
        self.assertEqual(sorted_products, list(Product.objects.all()))
        self.assertEqual(len(sorted_products), Product.objects.count())
