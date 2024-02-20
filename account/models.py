from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class TimeBasedModel(models.Model):
    class Meta:
        abstract = True

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class City(TimeBasedModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Город",
        null=True,
    )
    domain = models.CharField(
        max_length=255,
        verbose_name="Домен",
        null=True,
    )
    address = models.CharField(
        max_length=256,
        verbose_name="Адрес",
        null=True,
    )
    number = models.BigIntegerField(
        verbose_name="Номер телефона",
        default=0,
    )
    how_to_get_office = models.CharField(
        verbose_name="Как добраться до офиса",
        null=True,
        max_length=512,
    )
    schedule = models.TextField(
        verbose_name="График работы",
        default="Отсутствует",
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.name


class CityGroup(TimeBasedModel):
    name = models.CharField(max_length=255, verbose_name="Город")
    main_city = models.ForeignKey(
        "City",
        on_delete=models.SET_NULL,
        null=True,
        related_name="main_city_for_group",
        verbose_name="Главный город",
    )
    cities = models.ManyToManyField(
        City,
        related_name="city_group",
        verbose_name="Города",
    )

    class Meta:
        verbose_name = "Группа городов"
        verbose_name_plural = "Группы городов"


class CustomUser(AbstractUser):
    phone = models.CharField(verbose_name="Номер телефона", max_length=16, null=True)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, related_name="customers"
    )
    is_customer = models.BooleanField(
        verbose_name="Покупатель ли юзер?",
        default=False,
    )
