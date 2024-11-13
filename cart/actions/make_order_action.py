from django.db import transaction
from django.db.models import F, QuerySet

from api.serializers import OrderSerializer
from cart.models import CartItem, Order, ProductsInOrder
from shop.models import Price, ProductFrequenlyBoughtTogether

from crm_integration.abs import CRMInterface

class MakeOrderAction:
    _serializer_class = OrderSerializer
    _crm_api_class = None

    @classmethod
    def execute(
        cls,
        data,
        cart_items: QuerySet[CartItem],
        city_domain: str = None,
        order_serializer_class=None,
        crm_api_class: CRMInterface = None,
    ):
        if order_serializer_class is not None:
            cls._serializer_class = order_serializer_class

        if crm_api_class is not None:
            cls._crm_api_class = crm_api_class

        serializer = cls._serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        total = 0
        with transaction.atomic():
            order: Order = serializer.save()
            for item in cart_items:

                # Обновляем информацию о том, как часто покупают товар вместе с другими
                for other_item in cart_items.exclude(product__pk=item.product.pk):

                    friquenly_bought_together, _ = (
                        ProductFrequenlyBoughtTogether.objects.get_or_create(
                            product_from=item.product,
                            product_to=other_item.product,
                        )
                    )
                    friquenly_bought_together.purchase_count = F("purchase_count") + 1
                    friquenly_bought_together.save(update_fields=["purchase_count"])

                price = Price.objects.get(
                    city_group__cities__domain=city_domain, product=item.product
                )
                prod = ProductsInOrder.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=price.price,
                )

                item.delete()
                total += prod.price * prod.quantity
                del prod
                del price

            order.total = total
            order.save(update_fields=["total"])

        if cls._crm_api_class is not None:
            cls._crm_api_class.handle_order_creation(order, city_domain)

        return order
