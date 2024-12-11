from unittest.mock import patch
from django.test import TestCase
from django.db import transaction
from cart.actions import MakeOrderAction
from api.test_utils import SetupTestData
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError
from cart.models import CartItem, Order, ProductsInOrder
from shop.models import ProductFrequenlyBoughtTogether


class MakeOrderActionTestCase(TestCase):
    def setUp(self):
        self.user = SetupTestData.setup_custom_user("dummy_username", "dummy@mail.ru", "dummy_password")
        self.ctg = SetupTestData.setup_category("dummy_ctg")
        self.cg = SetupTestData.setup_city_group("dummy_city_group_name")
        self.product2 = SetupTestData.setup_product("Product 2", "Product 2", self.ctg)
        self.product1 = SetupTestData.setup_product("Product 1", "Product 1", self.ctg)
        self.city = SetupTestData.setup_city("dummy_city_name", self.cg, domain="dummy_domain")
        self.price1 = SetupTestData.setup_price(self.product1, "dummy_city_group_name", 799.00)
        self.price2 = SetupTestData.setup_price(self.product2, "dummy_city_group_name", 799.00)

        self.cart_item1 = CartItem.objects.create(product=self.product1, quantity=2, customer=self.user)
        self.cart_item2 = CartItem.objects.create(product=self.product2, quantity=1, customer=self.user)

        self.order_address = "улица Шишкова, Северный, Коминтерновский район, Воронеж, городской округ Воронеж, Воронежская область, Центральный федеральный округ, 394068, Россия"
        self.valid_data = {
            "phone": "+79936540978",
            "customer": self.user.pk,
            "address": self.order_address,
            "receiver_last_name": "dummy_last_name",
            "receiver_first_name": "dummy_first_name",
            "delivery_type": Order.DeliveryType.PICKUP,
        }

    @patch("api.serializers.OrderSerializer.is_valid", return_value=True)
    @patch("api.serializers.OrderSerializer.save")
    def test_execute_success(self, mock_save, mock_is_valid):
        order = Order.objects.create(
            total=0,
            customer=self.user,
            address=self.order_address,
            receiver_phone="+79982342523",
            receiver_email="reveiver@mail.ru",
            delivery_type=Order.DeliveryType.PICKUP,
            receiver_last_name="dummy_receiver_last_name",
            receiver_first_name="dummy_receiver_first_name",
        )
        mock_save.return_value = order

        result = MakeOrderAction.execute(
            data=self.valid_data,
            cart_items=CartItem.objects.all(),
            city_domain=self.city.domain,
        )
        self.assertIsInstance(result, Order)

        expected_total = self._calc_expected_total(order)

        self.assertEqual(result.total, expected_total)
        self.assertFalse(CartItem.objects.exists())

        products_in_order = ProductsInOrder.objects.filter(order=result)
        self.assertEqual(products_in_order.count(), 2)
    
    @staticmethod
    def _calc_expected_total(order: Order) -> int:
        expected_total = 0
        for prod in ProductsInOrder.objects.filter(order=order):
            expected_total += prod.price * prod.quantity

        return expected_total

    @patch("api.serializers.OrderSerializer.is_valid")
    def test_execute_invalid_data(self, mock_is_valid):
        mock_is_valid.side_effect = IntegrityError("Invalid data")
        with self.assertRaises(IntegrityError):
            MakeOrderAction.execute(
                data=self.valid_data,
                cart_items=CartItem.objects.all(),
                city_domain=self.city.domain,
            )

    @patch("crm_integration.tasks.create_order_in_crm_task.delay")
    def test_execute_crm_integration(self, mock_create_order_in_crm_task):
        order = Order.objects.create(
            total=0,
            customer=self.user,
            address=self.order_address,
            receiver_phone="+79982342523",
            receiver_email="reveiver@mail.ru",
            delivery_type=Order.DeliveryType.PICKUP,
            receiver_last_name="dummy_receiver_last_name",
            receiver_first_name="dummy_receiver_first_name",
        )
        MakeOrderAction.execute(
            data=self.valid_data,
            cart_items=CartItem.objects.all(),
            city_domain=self.city.domain,
        )
        mock_create_order_in_crm_task.assert_called_once()

    def test_update_frequently_bought_together(self):
        self.assertFalse(ProductFrequenlyBoughtTogether.objects.exists())
        MakeOrderAction.execute(
            data=self.valid_data,
            cart_items=CartItem.objects.all(),
            city_domain=self.city.domain,
        )
        self.assertTrue(ProductFrequenlyBoughtTogether.objects.exists())


    def test_transaction_atomic(self):
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                MakeOrderAction.execute(
                    data={},
                    cart_items=CartItem.objects.all(),
                    city_domain=self.city.domain,
                )

        self.assertTrue(CartItem.objects.exists())
        self.assertFalse(Order.objects.exists())
