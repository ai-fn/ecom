from decimal import Decimal
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.request import Request
from api.test_utils import send_request
from cart.models import Order, ProductsInOrder
from shop.models import Review, Product, Brand, Category
from api.serializers import ReviewSerializer
from django.urls import reverse


CustomUser = get_user_model()

class ReviewSerializerTestCase(APITestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Test Brand", slug="test-brand")

        self.category = Category.objects.create(name="Test Category", slug="test-category")

        self.product = Product.objects.create(
            title="Test Product",
            category=self.category,
            brand=self.brand,
            slug="test-product",
            article="123456789",
        )

        self.user = CustomUser.objects.create_user(
            username="testuser", password="testpass", email="testuser@gmail.com"
        )

        self.order = Order.objects.create(
            customer=self.user, total=100.00, address="123 Test St"
        )
        ProductsInOrder.objects.create(product=self.product, order=self.order, quantity=12, price=Decimal("120.00"))

    def test_create_review_success(self):
        """Тест успешного создания отзыва"""
        data = {
            "product": self.product.id,
            "rating": 5,
            "review": "Great product!"
        }
        factory = APIRequestFactory()
        request = factory.post(reverse('api:review-list'), data, format='json')
        force_authenticate(request, user=self.user)
        request = Request(request)
        serializer = ReviewSerializer(data=data, context={"request": request})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        review = serializer.save()

        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review, "Great product!")

    def test_create_review_without_purchase(self):
        """Тест создания отзыва без покупки продукта"""

        other_user = CustomUser.objects.create_user(
            username="otheruser", password="testpass", email="testuser@yandex.ru"
        )

        data = {
            "product": self.product.id,
            "rating": 4,
            "review": "Good product, but didn't buy it."
        }

        self.client.force_authenticate(user=other_user)
        response  = send_request(self.client.post, reverse('api:review-list'), data, format='json')
        self.assertEqual(response.status_code, 400)

        error_message = response.data['non_field_errors'][0]
        self.assertEqual(error_message, "You can only leave a review for products you have purchased.")

    def test_create_review_without_user(self):
        """Тест создания отзыва без указания пользователя в данных"""
        data = {
            'product': self.product.id,
            'rating': 5,
            'review': 'Trying to review without user'
        }
        response = send_request(self.client.post, reverse('api:review-list'), data, format='json')

        self.assertEqual(response.status_code, 401)

    def test_to_representation(self):
        """Тест корректности данных, возвращаемых сериализатором"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            review="Good product"
        )
        serializer = ReviewSerializer(review)

        expected_data = {
            "id": review.id,
            "product": self.product.id,
            "user": {
                "id": self.user.id,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "middle_name": self.user.middle_name,
                "is_active": self.user.is_active,
            },
            "rating": 4,
            "review": "Good product",
            "created_at": timezone.localtime(review.created_at).isoformat(),
            "is_active": review.is_active,
        }

        self.assertEqual(serializer.data, expected_data)
