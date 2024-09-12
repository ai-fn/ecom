import io
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from api.serializers import CategoryDocumentSerializer, ProductDocumentSerializer
from shop.models import Brand, Category, Product
from PIL import Image
from django.core.files.base import ContentFile


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
        self.assertTrue('image' in data)

    def test_deserialization(self):
        serializer = CategoryDocumentSerializer(data=self.category_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['id'], self.category_data['id'])
        self.assertEqual(validated_data['name'], self.category_data['name'])
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
