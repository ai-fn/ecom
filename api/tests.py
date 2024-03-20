import os
import pandas as pd
from rest_framework import test, status

from tempfile import NamedTemporaryFile

from django.urls import reverse
from django.conf import settings

from shop.models import Product, ProductImage
from account.models import CustomUser

# Create your tests here.


class TestUploadView(test.APITestCase):

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_superuser(
            email="dummy@gmail.com",
            password="dummy",
            username="dummy-users",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

        self.basename = "output.xlsx"
        self.upload_product_params = {"type": "PRODUCTS"}
        build_upload_url = lambda url, params: f"%s?%s" % (
            url,
            "?".join([f'{k}={"+".join(v.split())}' for k, v in params.items()]),
        )
        self.upload_url = build_upload_url(
            reverse("upload_products", args=[self.basename]), self.upload_product_params
        )
        self.temp_files_path = "/code/media/tmp/"

    def test_upload_products_only_for_staff(self):
        self.user1 = CustomUser.objects.create(
            email="dummy1@gmail.com",
            password="dummy",
            username="dummy-users1",
            is_staff=False,
        )
        self.client.force_authenticate(user=self.user)
        with open(os.path.join(self.temp_files_path, self.basename), "rb") as file_obj:
            self.client.force_authenticate(user=self.user1)
            response = self.client.put(self.upload_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.client.force_authenticate(user=self.user)
            response = self.client.put(self.upload_url, {"file": file_obj})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
