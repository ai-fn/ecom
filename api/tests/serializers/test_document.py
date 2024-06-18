import io
from django.test import TestCase
from account.models import CustomUser
from api.serializers import ImageSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from api.serializers import ReviewDocumentSerializer, CategoryDocumentSerializer, ProductDocumentSerializer
from shop.models import Brand, Category, Product, Review
from PIL import Image
from django.core.files.base import ContentFile


class ImageSerializerTest(TestCase):
    def test_image_field(self):
        image = io.BytesIO()
        Image.new('RGB', (100, 100)).save(image, format='JPEG')
        image.seek(0)
        image_file = SimpleUploadedFile("test_image.jpg", image.getvalue(), content_type="image/jpeg")
        
        data = {'image': image_file}
        serializer = ImageSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data['image'].name, "test_image.jpg")


class CategoryDocumentSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        image = io.BytesIO()
        Image.new('RGB', (100, 100)).save(image, format='JPEG')
        image.seek(0)
        cls.image_file = SimpleUploadedFile("test_image.jpg", image.getvalue(), content_type="image/jpeg")
        
        cls.category = Category.objects.create(
            id=1,
            name='Test Category',
            slug='test-category',
            parent=None,
            image=cls.image_file,
            is_visible=True,
            is_popular=True,
            order=1
        )
        cls.category_data = {
            'id': cls.category.id,
            'name': cls.category.name,
            'slug': cls.category.slug,
            'is_visible': cls.category.is_visible,
            'image': cls.category.image,
        }

    def test_serialization(self):
        serializer = CategoryDocumentSerializer(instance=self.category)
        data = serializer.data
        self.assertEqual(data['id'], self.category_data['id'])
        self.assertEqual(data['name'], self.category_data['name'])
        self.assertEqual(data['slug'], self.category_data['slug'])
        self.assertEqual(data['is_visible'], self.category_data['is_visible'])
        self.assertTrue('image' in data)

    def test_deserialization(self):
        serializer = CategoryDocumentSerializer(data=self.category_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['id'], self.category_data['id'])
        self.assertEqual(validated_data['name'], self.category_data['name'])
        self.assertEqual(validated_data['slug'], self.category_data['slug'])
        self.assertEqual(validated_data['is_visible'], self.category_data['is_visible'])
        self.assertEqual(validated_data['image'].name, self.category_data['image'].name)


class ProductDocumentSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        image = io.BytesIO()
        Image.new('RGB', (100, 100)).save(image, format='JPEG')
        image.seek(0)
        cls.image_file = ContentFile(image.read(), 'test_image.jpg')

        cls.category = Category.objects.create(name='Test Category', slug='test-category', is_visible=True, order=1)
        cls.brand = Brand.objects.create(name='Test Brand', slug='test-brand', order=1)
        cls.product = Product.objects.create(
            id=1,
            title="Test Product",
            description="Test Description",
            slug="test-product",
            category=cls.category,
            brand=cls.brand,
            catalog_image=cls.image_file,
            search_image=cls.image_file,
            original_image=cls.image_file,
            in_stock=True,
            is_popular=True,
            is_new=True,
            priority=10,
            article="TEST123"
        )

    def test_serialization(self):
        serializer = ProductDocumentSerializer(instance=self.product)
        data = serializer.data
        self.assertEqual(data['id'], self.product.id)
        self.assertEqual(data['title'], self.product.title)
        self.assertEqual(data['description'], self.product.description)
        self.assertEqual(data['slug'], self.product.slug)
        self.assertEqual(data['category_slug'], self.product.category.slug)

    def test_deserialization(self):
        data = {
            'id': self.product.id,
            'title': self.product.title,
            'description': self.product.description,
            'slug': f"{self.product.slug}-{self.product.id}",
            'category_slug': self.category.slug,
        }
        serializer = ProductDocumentSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['title'], data['title'])
        self.assertEqual(validated_data['description'], data['description'])
        self.assertEqual(validated_data['slug'], data['slug'])


class ReviewDocumentSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Test Category', slug='test-category', is_visible=True, order=1)
        cls.brand = Brand.objects.create(name='Test Brand', slug='test-brand', order=1)
        cls.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            category=cls.category,
            brand=cls.brand,
            article="TEST123"
        )
        cls.user = CustomUser.objects.create(first_name="John", last_name="Doe", middle_name="Smith")
        cls.review = Review.objects.create(
            product=cls.product,
            user=cls.user,
            rating=5,
            review="Excellent product!"
        )

    def test_serialization(self):
        serializer = ReviewDocumentSerializer(instance=self.review)
        data = serializer.data
        self.assertEqual(data['product'].title, self.product.title)
        self.assertEqual(data['product'].slug, self.product.slug)
        self.assertEqual(data['user'].first_name, self.user.first_name)
        self.assertEqual(data['user'].last_name, self.user.last_name)
        self.assertEqual(data['user'].middle_name, self.user.middle_name)
        self.assertEqual(data['rating'], self.review.rating)
        self.assertEqual(data['review'], self.review.review)

    def test_deserialization(self):
        data = {
            'product': {'title': self.product.title, 'slug': self.product.slug},
            'user': {'first_name': self.user.first_name, 'last_name': self.user.last_name, 'middle_name': self.user.middle_name},
            'rating': 5,
            'review': 'Excellent product!',
        }
        serializer = ReviewDocumentSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['product']['title'], data['product']['title'])
        self.assertEqual(validated_data['product']['slug'], data['product']['slug'])
        self.assertEqual(validated_data['user']['first_name'], data['user']['first_name'])
        self.assertEqual(validated_data['user']['last_name'], data['user']['last_name'])
        self.assertEqual(validated_data['user']['middle_name'], data['user']['middle_name'])
        self.assertEqual(validated_data['rating'], data['rating'])
        self.assertEqual(validated_data['review'], data['review'])
