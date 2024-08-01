import unittest
from unittest.mock import patch, MagicMock
from django.conf import settings
from loguru import logger
from account.models import CustomUser
from bitrix_app.services.bitrix_service import Bitrix24API
from cart.models import Order


class TestBitrix24API(unittest.TestCase):

    @patch("requests.get")
    def test_get_allowed_fields(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "TITLE": {"type": "string", "isRequired": False},
                "STATUS_ID": {"type": "string", "isRequired": False},
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        api = Bitrix24API()
        fields = api.get_allowed_fields()
        self.assertIn("TITLE", fields)
        self.assertIn("STATUS_ID", fields)
        self.assertEqual(fields["TITLE"]["type"], "string")
        self.assertEqual(fields["STATUS_ID"]["type"], "crm_status")

    @patch("requests.get")
    def test_retrieve(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": {"ID": "1", "TITLE": "Test Lead"}}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        api = Bitrix24API()
        lead, status_code = api.retrieve(1)
        self.assertEqual(status_code, 200)
        self.assertEqual(lead["result"]["TITLE"], "Test Lead")

    @patch("requests.post")
    def test_add_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": 1}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = Bitrix24API()
        lead_data = {"TITLE": "New Lead"}
        result, status_code = api.add_lead(lead_data)
        self.assertEqual(status_code, 200)
        self.assertEqual(result["result"], 1)

    @patch("requests.post")
    def test_update_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = Bitrix24API()
        lead_data = {"TITLE": "Updated Lead"}
        result, status_code = api.update_lead(1, lead_data)
        self.assertEqual(status_code, 200)
        self.assertTrue(result["result"])

    @patch("requests.post")
    def test_delete_lead(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api = Bitrix24API()
        result, status_code = api.delete_lead(1)
        self.assertEqual(status_code, 200)
        self.assertTrue(result["result"])

    @patch("requests.get")
    def test_get_leads_by_period(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [{"ID": "1", "TITLE": "Test Lead"}]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        api = Bitrix24API()
        leads = api.get_leads_by_period(weeks=1)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["TITLE"], "Test Lead")

    @patch("bitrix_app.services.Bitrix24API.post_response")
    @patch("bitrix_app.services.Bitrix24API.get_default_lead_user")
    def test_create_lead_for_order(
        self, mock_get_default_lead_user, mock_post_response
    ):
        mock_get_default_lead_user.return_value = {"ID": "123"}

        mock_post_response.return_value = ({"result": {"ID": "456"}}, 200)

        customer = CustomUser(
            first_name="Иван",
            middle_name="Иванович",
            last_name="Иванов",
            phone="+79991234567",
        )
        order = Order(
            customer=customer,
            total=5000,
            address="Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
        )

        domain = "example.com"

        api = Bitrix24API()
        result = api.create_lead_for_order(order, domain)

        expected_lead_data = {
            "fields": {
                "TITLE": "+79991234567 Заказ от Иван Иванов",
                "ASSIGNED_BY_ID": "123",
                "OPENED": "Y",
                "STATUS_ID": "NEW",
                "ADDRESS": "Патриаршие пруды, 48, Пресненский район, Москва, Центральный федеральный округ, 123001, Россия",
                "NAME": "Иван",
                "SECOND_NAME": "Иванович",
                "LAST_NAME": "Иванов",
                "CURRENCY_ID": "RUB",
                "OPPORTUNITY": 5000,
                "PHONE": [{"VALUE": "+79991234567", "VALUE_TYPE": "WORK"}],
                "WEB": [{"VALUE": "example.com", "VALUE_TYPE": "WORK"}],
            },
            "params": {"REGISTER_SONET_EVENT": "Y"},
        }
        mock_post_response.assert_called_once_with(
            f"{api.lead_add_webhook_url}/crm.lead.add.json", expected_lead_data
        )

        self.assertEqual(result, {"result": {"ID": "456"}})


if __name__ == "__main__":
    unittest.main()
