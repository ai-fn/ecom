from django.db import models

from account.models import CustomUser, TimeBasedModel
from shop.models import Product


class Order(TimeBasedModel):
    customer = models.ForeignKey(
        CustomUser,
        related_name="customer",
        on_delete=models.CASCADE,
        verbose_name="Покупатель",
    )
    products = models.ManyToManyField(
        Product, verbose_name="Товары", blank=True, through="ProductsInOrder"
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время создания"
    )
    address = models.CharField(
        verbose_name="Адрес", max_length=255
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.customer} - {self.created}"


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
        verbose_name="Торвар",
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Продукт в корзине пользователя"
        verbose_name_plural = "Продукт в корзине пользователя"
