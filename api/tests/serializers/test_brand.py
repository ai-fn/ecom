from django.test import TestCase
from rest_framework.test import APIClient
from shop.models import Brand
from api.serializers import BrandSerializer
from django.core.files.uploadedfile import SimpleUploadedFile


class BrandSerializerTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.icon_file = SimpleUploadedFile(
            "icon.png", b"file_content", content_type="image/png"
        )
        self.brand_with_icon = Brand.objects.create(
            name="Brand With Icon", icon=self.icon_file, order=1, slug="brand-with-icon"
        )
        self.brand_without_icon = Brand.objects.create(
            name="Brand Without Icon", order=2, slug="brand-without-icon"
        )

    def test_brand_with_icon(self):
        serializer = BrandSerializer(self.brand_with_icon)
        data = serializer.data

        self.assertEqual(data["id"], self.brand_with_icon.id)
        self.assertEqual(data["name"], self.brand_with_icon.name)
        self.assertIsNotNone(data["icon"])
        self.assertEqual(data["slug"], self.brand_with_icon.slug)

    def test_brand_without_icon(self):
        serializer = BrandSerializer(self.brand_without_icon)
        data = serializer.data

        self.assertEqual(data["id"], self.brand_without_icon.id)
        self.assertEqual(data["name"], self.brand_without_icon.name)
        self.assertIsNone(data["icon"])
        self.assertEqual(data["slug"], self.brand_without_icon.slug)
