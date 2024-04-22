from django.db import models
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
