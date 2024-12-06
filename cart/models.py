from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from account.models import City, CustomUser, TimeBasedModel
from shop.models import Product


class OrderStatus(models.TextChoices):
    PENDING = 'P', _('Создан')
    PROCESSING = 'PR', _('В обработке')
    SHIPPED = 'S', _('Отправлен')
    DELIVERED = 'D', _('Доставлен')

class Order(TimeBasedModel):

    class DeliveryType(models.TextChoices):
        DELIVERY = "delivery", _("Доставка")
        PICKUP = "pickup", _("Пункт выдачи")

    customer = models.ForeignKey(
        CustomUser,
        related_name="customer",
        on_delete=models.PROTECT,
        verbose_name="Покупатель",
    )
    receiver_first_name = models.CharField(
        _("Имя получателя"),
        max_length=100,
    )
    receiver_last_name = models.CharField(
        _("Фамилия получателя"),
        max_length=100,
    )
    receiver_phone = models.CharField(
        verbose_name=_("Номер телефона получателя"),
        null=True,
        blank=True,
        max_length=16,
        help_text=_("В формате +7xxxxxxxxxx"),
    )
    receiver_email = models.EmailField(
        _("Почта"),
        help_text=_("Адрес электронной почты получателя"),
        blank=True,
        null=True,
    )
    delivery_type = models.CharField(
        _("Тип доставки"),
        max_length=30,
        choices=DeliveryType.choices,
    )
    products = models.ManyToManyField(
        Product, verbose_name="Товары", blank=True, through="ProductsInOrder"
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма заказа"
    )
    address = models.CharField(verbose_name=_("Адрес"), max_length=1024)
    status = models.CharField(
        choices=OrderStatus.choices,
        verbose_name=_("Статус заказа"),
        default=OrderStatus.PENDING,
        max_length=20,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ("customer", "-created_at")

    def clean(self) -> None:
        if self.status not in OrderStatus.values:
            raise ValidationError(_(f"Некорректный статус: {self.status}"))
        return super().clean()

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
    
    class Meta:
        verbose_name = _("Товар в заказе")
        verbose_name_plural = _("Товары в заказе")
        ordering = ("order", "-created_at")


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
        unique_together = (("customer", "product"), )


class PickupPoint(TimeBasedModel):
    address = models.CharField(_("Адрес"), max_length=512, unique=True)
    coord_x = models.DecimalField(
        _("X координата"),
        max_digits=9,
        decimal_places=6,
    )
    coord_y = models.DecimalField(
        _("Y координата"),
        max_digits=9,
        decimal_places=6,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        verbose_name=_("Город")
    )
    phone = models.CharField(
        verbose_name=_("Номер телефона"),
        null=True,
        blank=True,
        max_length=16,
        help_text=_("В формате +7xxxxxxxxxx")
    )

    class Meta:
        verbose_name = _("Пункт выдачи")
        verbose_name_plural = _("Пункты выдачи")
        unique_together = (("coord_x", "coord_y"),)
    
    def __str__(self) -> str:
        return f"Пункт выдачи #{self.id}"


class PickupPointSchedule(TimeBasedModel):

    schedule = models.CharField(_("График работы"), max_length=256)
    title = models.CharField(_("Заголовок"), max_length=128, blank=True, null=True)
    order = models.PositiveIntegerField(
        _("Порядковый номер"), default=0, blank=True, null=True
    )
    pickup_point = models.ForeignKey(
        PickupPoint,
        on_delete=models.CASCADE,
        verbose_name=_("Пункт выдачи"),
        related_name="schedules",
    )

    class Meta:
        verbose_name = _("График работы пункта выдачи")
        verbose_name_plural = _("Графики работы пунктов выдачи")
        ordering = ("pickup_point", "order", "-created_at")
        indexes = [
            models.Index(fields=["title"], name="pp_schedule_title_idx"),
            models.Index(fields=["schedule"], name="pp_schedule_schedule_idx"),
        ]

    def __str__(self) -> str:
        return f"#{self.id} График работы пункта выдачи '{self.pickup_point.pk}'"
