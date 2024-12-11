from unittest.mock import patch
from asgiref.sync import async_to_sync
from django.test import TestCase
from account.models import City, CustomUser
from cart.models import Order, ProductsInOrder
from crm_integration.actions.bitrix import CreateOrderAction
from api.test_utils import SetupTestData


class TestBitrixAPI(TestCase):

    @classmethod
    def setUpTestData(cls):
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
            address="улица Шишкова, Воронеж",
        )

        cls.ctg = SetupTestData.setup_category("dummy_ctg")
        cls.prod = SetupTestData.setup_product(
            "dummy-title", "dummy-article", category=cls.ctg
        )
        cls.ops = ProductsInOrder.objects.create(
            product=cls.prod, price=5000, quantity=1, order=cls.order
        )
        cls.city_group = SetupTestData.setup_city_group(name="dummy_city_group")
        cls.city = SetupTestData.setup_city(name="test_city", city_group=cls.city_group, domain="example.com")

    @patch("crm_integration.actions.bitrix.base.BaseBitrixAction.post_response")
    def test_add_lead(self, mock_post_response):
        mock_post_response.return_value = ({"result": 1}, 200)
        action = CreateOrderAction()

        lead_data = {"TITLE": "New Lead"}
        result, status_code = async_to_sync(action.add_lead)(lead_data)

        self.assertEqual(status_code, 200)
        self.assertEqual(result["result"], 1)

    @patch("crm_integration.actions.bitrix.base.BaseBitrixAction.post_response")
    def test_update_lead(self, mock_post_response):
        mock_post_response.return_value = ({"result": True}, 200)
        action = CreateOrderAction()

        lead_data = {"TITLE": "Updated Lead"}
        result, status_code = async_to_sync(action.update_lead)(1, lead_data)

        self.assertEqual(status_code, 200)
        self.assertTrue(result["result"])

    @patch("crm_integration.actions.bitrix.base.BaseBitrixAction.post_response")
    @patch("crm_integration.actions.bitrix.order_action.CreateOrderAction.get_default_lead_user")
    def test_create_lead_for_order(self, mock_get_default_lead_user, mock_post_response):
        mock_get_default_lead_user.return_value = {"ID": "123"}
        mock_post_response.return_value = ({"result": {"ID": "456"}}, 200)

        domain = self.city.domain
        action = CreateOrderAction()
        result = async_to_sync(action.create_lead_for_order)(self.order, domain)

        self.assertEqual(result, mock_post_response.return_value[0])
