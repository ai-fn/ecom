from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from shop.models import Brand, Product, Price, City, CityGroup, Category
from cart.models import CartItem
from api.serializers import CartItemSerializer, SimplifiedCartItemSerializer

User = get_user_model()


class CartItemSerializerTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.category = Category.objects.create(name="Test Category", order=1, slug="test-category-slug")
        self.brand = Brand.objects.create(name='Test Brand', slug='test-brand', order=1)
        self.product = Product.objects.create(
            id=1,
            title="Test Product",
            description="Test Description",
            slug="test-product",
            category=self.category,
            brand=self.brand,
            in_stock=True,
            is_popular=True,
            is_new=True,
            priority=10,
            article="TEST123"
        )
        self.city_group = CityGroup.objects.create(name="Воронеж Group")
        self.city = City.objects.create(name="Воронеж", domain="voronezh.krov.market")
        self.city_group.cities.add(self.city)
        self.cart_item = CartItem.objects.create(
            customer=self.user, product=self.product, quantity=1
        )

    def test_cart_item_serializer_create(self):
        data = {"product_id": self.product.id, "quantity": 2}
        request = self.factory.post("/cart/", data)
        request.query_params = {"city_domain": "voronezh.krov.market"}
        request.user = self.user
        serializer = CartItemSerializer(data=data, context={"request": request})

        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()

        self.assertEqual(cart_item.customer, self.user)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)

        self.assertIsNone(serializer.data["product"].get("city_price"))
        
        Price.objects.create(product=self.product, city_group=self.city_group, price=100.99)
        serializer = CartItemSerializer(data=data, context={"request": request})
        serializer.is_valid()

        self.assertIsNotNone(serializer.data["product"].get("city_price"))

    def test_cart_item_serializer_update(self):
        data = {"quantity": 3}
        serializer = CartItemSerializer(self.cart_item, data=data, partial=True)

        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()

        self.assertEqual(cart_item.quantity, 3)

    def test_cart_item_serializer_duplicate_create(self):
        data = {"product_id": self.product.id, "quantity": 4}
        request = self.factory.post("/cart/", data)
        request.user = self.user
        serializer = CartItemSerializer(data=data, context={"request": request})

        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()

        self.assertEqual(
            CartItem.objects.count(), 1
        )
        self.assertEqual(cart_item.quantity, 4)

    def test_simplified_cart_item_serializer(self):
        data = {"product_id": self.product.id, "quantity": 5}
        serializer = SimplifiedCartItemSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save(
            customer=self.user
        )

        self.assertEqual(cart_item.customer, self.user)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 5)
