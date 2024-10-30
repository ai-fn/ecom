from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from loguru import logger
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
        self.product_2 = Product.objects.create(
            id=2,
            title="Test Product 2",
            description="Test Description",
            slug="test-product-2",
            category=self.category,
            brand=self.brand,
            in_stock=True,
            is_popular=True,
            is_new=True,
            priority=10,
            article="TEST2"
        )
        self.city_group = CityGroup.objects.create(name="Воронеж Group")
        self.city = City.objects.create(name="Воронеж", domain="voronezh.domain.com")
        self.city_group.cities.add(self.city)

    def test_cart_item_serializer_create(self):
        dummy_domain = "voronezh.domain.com"
        data = {"product_id": self.product.id, "quantity": 2}
        request = self.factory.post("/cart/", data)
        request.query_params = {"city_domain": dummy_domain}
        request.user = self.user
        serializer = CartItemSerializer(data=data, context={"request": request, "city_domain": dummy_domain})

        self.assertTrue(serializer.is_valid())
        cart_item = serializer.save()

        self.assertEqual(cart_item.customer, self.user)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)

        self.assertIsNone(serializer.data["product"]["city_price"])
        
        price = Price.objects.create(product=self.product, city_group=self.city_group, price=100.99)
        cart_item.refresh_from_db()
        serializer = CartItemSerializer(instance=cart_item, context={"request": request, "city_domain": dummy_domain})
        self.assertEqual(serializer.data["product"]["city_price"], str(price.price))

    def test_cart_item_serializer_update(self):
        cart_item = CartItem.objects.create(
            product=self.product, customer=self.user, quantity=5
        )

        updated_data = {"quantity": 15}
        serializer = CartItemSerializer(data=updated_data, partial=True)

        self.assertTrue(serializer.is_valid())
        cart_item = serializer.update(cart_item, serializer.validated_data)
        
        self.assertEqual(cart_item.quantity, 15)

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
        cart_item = CartItem.objects.get(product__id=data['product_id']) 
        self.assertEqual(cart_item.quantity, 4)

    def test_simplified_cart_item_serializer(self):
        data = {"product_id": self.product.id, "quantity": 5}
        serializer = SimplifiedCartItemSerializer(data=data)

        self.assertTrue(serializer.is_valid())

        serializer.save(customer=self.user)
        
        cart_item = CartItem.objects.get(product__id=data['product_id']) 

        self.assertEqual(cart_item.customer, self.user)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 5)
