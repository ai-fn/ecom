from django.db import transaction
from django.db.models import F, QuerySet

from api.serializers import OrderSerializer
from cart.models import CartItem, Order, ProductsInOrder
from crm_integration.tasks import create_order_in_crm_task
from shop.models import Price, ProductFrequenlyBoughtTogether


class MakeOrderAction:
    """
    Класс для выполнения действия по созданию заказа на основе данных корзины и переданных параметров.
    """

    _serializer_class = OrderSerializer

    @classmethod
    def execute(
        cls,
        data: dict,
        cart_items: QuerySet[CartItem],
        city_domain: str = None,
        order_serializer_class=None,
    ) -> Order:
        """
        Выполняет процесс создания заказа.

        :param data: Данные для сериализации заказа.
        :type data: dict
        :param cart_items: QuerySet с элементами корзины.
        :type cart_items: QuerySet[CartItem]
        :param city_domain: Домен города для определения цены.
        :type city_domain: str, optional
        :param order_serializer_class: Альтернативный сериализатор заказа.
        :type order_serializer_class: Serializer, optional
        :param crm_api_class: API-класс для интеграции с CRM.
        :type crm_api_class: CRMInterface, optional
        :return: Созданный заказ.
        :rtype: Order
        :raises ValidationError: Если данные для заказа не валидны.
        """
        if order_serializer_class is not None:
            cls._serializer_class = order_serializer_class

        serializer = cls._serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        total = 0
        with transaction.atomic():
            order: Order = serializer.save()

            for item in cart_items:
                # Обновление информации о часто покупаемых вместе товарах
                for other_item in cart_items.exclude(product__pk=item.product.pk):
                    frequently_bought_together, _ = ProductFrequenlyBoughtTogether.objects.get_or_create(
                        product_from=item.product,
                        product_to=other_item.product,
                    )
                    frequently_bought_together.purchase_count = F("purchase_count") + 1
                    frequently_bought_together.save(update_fields=["purchase_count"])

                # Получение цены продукта для текущего города
                price = Price.objects.get(
                    city_group__cities__domain=city_domain,
                    product=item.product,
                )

                # Создание записи о товаре в заказе
                prod = ProductsInOrder.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=price.price,
                )

                item.delete()  # Удаление элемента корзины
                total += prod.price * prod.quantity

            # Обновление общей суммы заказа
            order.total = total
            order.save(update_fields=["total"])

        order_data = OrderSerializer(instance=order).data
        create_order_in_crm_task.delay(order_data)

        return order
