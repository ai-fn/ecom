from django.test import TestCase
from django.urls import reverse
from api.test_utils import SetupTestData
from shop.models import Price, Product

from django.conf import settings


class TestProductViewSet(TestCase):

    def setUp(self):
        self.s = SetupTestData()
        self.c = self.s.setup_city("Москва", domain=settings.BASE_DOMAIN)
        self.cg = self.s.setup_city_group("Московская область")
        self.cg.cities.add(self.c)

        ctg = self.s.setup_category("Dummy Category 777")
        self.popular_prods = sorted([
            self.s.setup_product(f"Very Popular Dummy Product {i}", f"dummy-article-{i}23LNVS", category=ctg, is_popular=True, priority=i*100)
            for i in range(1, 35)
        ], key=lambda x: (-x.priority, x.title, -x.created_at.timestamp()))
        self.products = Product.objects.all()

    def test_list_view(self):
        path = reverse("api:products-list")
        response = self.client.get(path).json()

        self.assertIn("count", response)
        self.assertIn("next", response)
        self.assertIn("previous", response)
        self.assertIn("results", response)
        self.assertIn("products", response["results"])
        self.assertIn("characteristics", response["results"])
        self.assertIn("brands", response["results"])
        self.assertIn("categories", response["results"])
        self.assertIn("smallest_price", response["results"])
        self.assertIn("greatest_price", response["results"])

    def test_list_view_with_domain_without_prices(self):
        path = reverse("api:products-list")
        params = {"city_domain": self.c.domain}
        response = self.client.get(path, params).json()
        self.assertEqual(response["results"]["products"], [])

    def test_list_views_with_domain_with_prices(self):
        path = reverse("api:products-list")
        params = {"city_domain": self.c.domain}
        prices = {}
        for i, prod in enumerate(self.products, 1):
            price = self.s.setup_price(prod, self.cg.name, 200*i)
            prices[prod.id] = {
                "price": f"{price.price or 0:.2f}",
                "old_price": f"{price.old_price:.2f}" if price.old_price else None,
            }

        response = self.client.get(path, params).json()
        self.assertEqual(response["count"], len(self.products))
        response_products = response["results"]["products"]
        for i in range(len(response["results"]["products"])):
            self.assertEqual(response_products[i]["id"], self.products[i].id)
            self.assertEqual(response_products[i]["city_price"], prices[self.products[i].id]["price"])
            self.assertEqual(response_products[i]["old_price"], prices[self.products[i].id]["old_price"])

    def test_popular_products_view(self):
        path = reverse("api:products-popular-products")
        response = self.client.get(path).json()
        self.assertIn("count", response)
        self.assertIn("next", response)
        self.assertIn("previous", response)
        self.assertIn("results", response)

    def test_popular_products_view_with_domain_without_prices(self):
        Price.objects.all().delete()
        path = reverse("api:products-popular-products")
        params = {"city_domain": self.c.domain}

        response = self.client.get(path, params).json()
        self.assertEqual(response["results"], [])
        self.assertIsNone(response["previous"])
        self.assertIsNone(response["next"])

    def test_popular_products_view_with_prices(self):
        path = reverse("api:products-popular-products")
        params = {"city_domain": self.c.domain}
        expected_count = Product.objects.filter(is_popular=True).count()
        prices = {}
        for idx, prod in enumerate(self.popular_prods, 1):
            price = self.s.setup_price(prod, self.cg.name, 100*idx)
            prices[prod.id] = {
                "product_id": prod.id,
                "price": f"{price.price or 0:.2f}",
                "old_price": f"{price.old_price:.2f}" if price.old_price else None,
            }

        response = self.client.get(path, params).json()
        self.assertEqual(expected_count, response["count"])

        for i in range(len(response["results"])):
            self.assertEqual(
                response["results"][i]["id"], 
                prices[self.popular_prods[i].id]["product_id"]
            )
            self.assertEqual(response["results"][i]["city_price"], prices[self.popular_prods[i].id]["price"])
            self.assertEqual(response["results"][i]["old_price"], prices[self.popular_prods[i].id]["old_price"])
