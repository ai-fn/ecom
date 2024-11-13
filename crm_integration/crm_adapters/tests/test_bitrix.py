from decimal import Decimal
from django.test import TestCase

from account.models import CustomUser
from api.test_utils import SetupTestData
from unittest.mock import patch, MagicMock
from cart.models import Order, ProductsInOrder
from crm_integration.crm_adapters import BitrixAPI


class TestBitrixAPI(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.customer = CustomUser.objects.create(
            first_name="Иван",
            middle_name="Иванович",
            last_name="Иванов",
            phone="+79991234567",
        )
        cls.order = Order.objects.create(
            total=5000,
            customer=cls.customer,
            receiver_last_name=cls.customer.last_name,
            receiver_first_name=cls.customer.first_name,
            address="Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
        )

        cls.ctg = SetupTestData.setup_category("dummy_ctg")
        cls.prod = SetupTestData.setup_product(
            "dummy-title", "dummy-article", category=cls.ctg
        )
        cls.ops = ProductsInOrder.objects.create(
            product=cls.prod, price=5000, quantity=1, order=cls.order
        )

    @patch("requests.post")
    def test_add_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 1}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = BitrixAPI
        lead_data = {"TITLE": "New Lead"}
        result, status_code = api._add_lead(lead_data)
        self.assertEqual(status_code, 200)
        self.assertEqual(result["result"], 1)

    @patch("requests.post")
    def test_update_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = BitrixAPI
        lead_data = {"TITLE": "Updated Lead"}
        result, status_code = api.update_lead(1, lead_data)
        self.assertEqual(status_code, 200)
        self.assertTrue(result["result"])

    @patch("crm_integration.crm_adapters.BitrixAPI.post_response")
    @patch("crm_integration.crm_adapters.BitrixAPI.get_default_lead_user")
    def test_create_lead_for_order(
        self, mock_get_default_lead_user, mock_post_response
    ):
        mock_get_default_lead_user.return_value = {"ID": "123"}

        mock_post_response.return_value = ({"result": {"ID": "456"}}, 200)

        domain = "example.com"

        api = BitrixAPI
        result = api.create_lead_for_order(self.order, domain)

        expected_lead_data = {
            "fields": {
                "TITLE": "+79991234567 Заказ от Иван Иванов",
                "ASSIGNED_BY_ID": "123",
                "OPENED": "N",
                "STATUS_ID": "NEW",
                "ADDRESS": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
                "NAME": "Иван",
                "UF_CRM_1725873647873": "Иван",
                "LAST_NAME": "Иванов",
                "CURRENCY_ID": "RUB",
                "OPPORTUNITY": float(self.order.total),
                "UF_CRM_1726038229797": float(self.order.total),
                "PHONE": [{"VALUE": "+79991234567", "VALUE_TYPE": "WORK"}],
                "WEB": [{"VALUE": "example.com", "VALUE_TYPE": "WORK"}],
                "UF_CRM_1586436329935": None,
                "COMMENTS": f"{self.ops.product.title}\n\tКоличество: {self.ops.quantity}\n\tЦена: {float(self.ops.price)}",
                "UF_CRM_1726050625737": f"{self.ops.product.title}\n\tКоличество: {self.ops.quantity}\n\tЦена: {float(self.ops.price)}",
            },
            "params": {"REGISTER_SONET_EVENT": "Y"},
        }
        mock_post_response.assert_called_once_with(
            f"{api.lead_add_webhook_url}/crm.lead.add.json", expected_lead_data
        )

        self.assertEqual(result, {"result": {"ID": "456"}})
