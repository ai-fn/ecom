import os

from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


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
    nominative_case = models.CharField(
        verbose_name="Именительный падеж", null=True, blank=True, max_length=128
    )
    genitive_case = models.CharField(
        verbose_name="Родительный падеж", null=True, blank=True, max_length=128
    )
    dative_case = models.CharField(
        verbose_name="Дательный падеж", null=True, blank=True, max_length=128
    )
    accusative_case = models.CharField(
        verbose_name="Винительный падеж", null=True, blank=True, max_length=128
    )
    instrumental_case = models.CharField(
        verbose_name="Творительный падеж", null=True, blank=True, max_length=128
    )
    prepositional_case = models.CharField(
        verbose_name="Предложный падеж",
        null=True,
        max_length=128,
    )
    population = models.PositiveBigIntegerField(
        verbose_name="Численность населения", default=0
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ("name",)
        indexes = [
            models.Index(fields=["name"], name="city_name_idx"),
            models.Index(fields=["domain"], name="city_domain_idx"),
            models.Index(fields=["address"], name="city_address_idx"),
        ]

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_default_city() -> "City":
        default_name = os.getenv("DEFAULT_CITY_NAME", "москва")
        city, _ = City.objects.get_or_create(name__iexact=default_name)
        return city


class CityGroup(TimeBasedModel):
    name = models.CharField(max_length=255, verbose_name="Название группы", unique=True)
    main_city = models.ForeignKey(
        "City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        indexes = [
            models.Index(fields=["name"], name="citygroup_name_idx"),
            models.Index(fields=["main_city"], name="citygroup_main_city_idx"),
        ]

    def __str__(self) -> str:
        return f"Группа {self.name}"


class CustomUser(AbstractUser):
    first_name = models.CharField(
        _("Имя"), max_length=35, blank=True, null=True
    )
    last_name = models.CharField(_("Фамилия "), max_length=35, blank=True, null=True)
    email = models.EmailField(_("Почта"), help_text=_("Адрес электронной почты"), blank=True, null=True)
    phone = models.CharField(
        verbose_name=_("Номер телефона"), null=True, blank=True, unique=True, max_length=16, help_text=_("In format +7xxxxxxxxxx")
    )
    address = models.CharField(_("Адрес"), max_length=1024, null=True, blank=True)
    is_customer = models.BooleanField(
        verbose_name=_("Покупатель ли юзер?"),
        default=False,
    )
    email_confirmed = models.BooleanField(
        default=False, verbose_name=_("Подтверждена ли почта")
    )
    middle_name = models.CharField(
        verbose_name=_("Отчество"), blank=True, null=True, max_length=35
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        indexes = [
            models.Index(fields=["phone"], name="customuser_phone_idx"),
            models.Index(fields=["address"], name="customuser_address_idx"),
        ]
    
    def __str__(self) -> str:
        return f"CustomUser({self.phone})"

    def delete(self, *args):

        if not self.is_active:
            pass
        else:
            self.is_active = False
            self.save(update_fields=["is_active", "first_name"])
