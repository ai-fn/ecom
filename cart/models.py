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
    region = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Область"
    )
    district = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Район"
    )
    city_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Город"
    )
    street = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Улица"
    )
    house = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Номер дома"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")

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
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена товара на момент заказа")

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
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Продукт в корзине пользователя"
        verbose_name_plural = "Продукт в корзине пользователя"
