from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import CustomUser, TimeBasedModel
from shop.models import Product


class OrderStatus(TimeBasedModel):
    name = models.CharField(max_length=128, verbose_name="Название статуса")

    def __str__(self) -> str:
        return f"Статус заказа: {self.name}"

    @staticmethod
    def get_created_status(*args, **kwargs):
        return OrderStatus.objects.get_or_create(name="Создан")[0]
    
    @staticmethod
    def get_created_pk(*args, **kwargs) -> int:
        return OrderStatus.get_created_status().pk

    class Meta:
        verbose_name = _("Статус заказа")
        verbose_name_plural = _("Статусы заказа")


class Order(TimeBasedModel):
    customer = models.ForeignKey(
        CustomUser,
        related_name="customer",
        on_delete=models.PROTECT,
        verbose_name="Покупатель",
    )
    products = models.ManyToManyField(
        Product, verbose_name="Товары", blank=True, through="ProductsInOrder"
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма заказа"
    )
    address = models.CharField(verbose_name=_("Адрес"), max_length=1024)
    status = models.ForeignKey(
        OrderStatus,
        verbose_name="Статус заказа",
        related_name="status",
        on_delete=models.PROTECT,
        default=OrderStatus.get_created_pk,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.customer} - {self.created_at}"


class ProductsInOrder(TimeBasedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Товар",
        related_name="count_in_order",
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name="Количество товара в заказе"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена товара на момент заказа"
    )

    def __str__(self) -> str:
        return f"Корзина {self.id}"


class CartItem(TimeBasedModel):
    customer = models.ForeignKey(
        CustomUser,
        related_name="cart",
        on_delete=models.CASCADE,
        verbose_name="Покупатель",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар",
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Продукт в корзине пользователя"
        verbose_name_plural = "Продукт в корзине пользователя"
