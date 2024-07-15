from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import TimeBasedModel
from shop.models import Product


class Article(TimeBasedModel):
    name = models.CharField(max_length=128, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Основной текст")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    products = models.ManyToManyField(Product, verbose_name="Товары", blank=True, related_name="articles")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.name


class Feedback(TimeBasedModel):
    
    name = models.CharField(_("Имя отправителя"), max_length=128)
    email = models.EmailField(_("Электронная почта"))
    message = models.TextField(_("Текст обратной связи"), max_length=2048)

    class Meta:
        verbose_name = _("Обратная связь")
        verbose_name_plural = _("Обратная связь")

    def __str__(self) -> str:
        return f"Feedback from {self.name} ({self.email})"
