from typing import Any
from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from unidecode import unidecode

from shop.utils import get_base_domain


class TimeBasedModel(models.Model):
    class Meta:
        abstract = True

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(_("Активность"), default=True)

    def save(self, *args, update_fields=None, **kwargs) -> None:
        update_fields = self._set_order(update_fields)
        update_fields = self._set_slug(update_fields)
        return super().save(*args, update_fields=update_fields, **kwargs)

    def _set_order(self: models.Model, update_fields):
        if hasattr(self, "order"):

            order = getattr(self, "order", None)
            if not order:
                order_value = (
                    self._meta.model.objects.order_by("order")
                    .values_list("order", flat=True)
                    .last()
                    or 0
                ) + 1
                setattr(self, "order", order_value)

                if self.pk:
                    update_fields = update_fields or tuple()
                    update_fields = {*update_fields, "order"}

        return update_fields

    def _set_slug(self: models.Model, update_fields=None):
        if hasattr(self, "slug"):

            slug = getattr(self, "slug", None)
            if not slug:
                value = getattr(self, "name", None) or getattr(self, "title", None)
                if value is not None:
                    slug_value = slugify(unidecode(value))
                    setattr(self, "slug", slug_value)

                if self.pk:
                    update_fields = update_fields or tuple()
                    update_fields = {*update_fields, "slug"}

        return update_fields


class City(TimeBasedModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Город",
        null=True,
        unique=True,
    )
    domain = models.CharField(
        max_length=255,
        verbose_name="Домен",
        null=True,
        unique=True,
    )
    population = models.PositiveBigIntegerField(
        verbose_name="Численность населения", default=0
    )
    city_group = models.ForeignKey(
        "CityGroup",
        verbose_name=_("Группа городов"),
        on_delete=models.SET_NULL,
        related_name="cities",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ("name",)
        indexes = [
            models.Index(fields=["name"], name="city_name_idx"),
            models.Index(fields=["domain"], name="city_domain_idx"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.domain:
            self.domain = f'{slugify(unidecode(self.name))}.{get_base_domain()}'

        return super().save(*args, **kwargs)

    @staticmethod
    def get_default_city() -> "City":
        default_name = settings.DEFAULT_CITY_NAME
        city, created = City.objects.get_or_create(name=default_name)
        if created:
            city.city_group = CityGroup.get_default_city_group()
            city.save()

        return city

    @staticmethod
    def get_default_city_pk() -> int:
        return CityGroup.get_default_city_group().pk


class CityGroup(TimeBasedModel):
    name = models.CharField(max_length=255, verbose_name="Название группы", unique=True)
    main_city = models.OneToOneField(
        "City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_in_group",
        verbose_name="Главный город",
    )

    class Meta:
        verbose_name = "Группа городов"
        verbose_name_plural = "Группы городов"
        indexes = [
            models.Index(fields=["name"], name="citygroup_name_idx"),
            models.Index(fields=["main_city"], name="citygroup_main_city_idx"),
        ]
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Группа {self.name}"

    @staticmethod
    def get_main_city_domain(domain: str) -> str | None:
        key = f"GET_MAIN_CITY_DOMAIN_{domain.upper()}"
        cached_data = cache.get(key)
        if not cached_data:
            cg = CityGroup.objects.filter(cities__domain=domain).first()
            cached_data = cg.main_city.domain if cg and cg.main_city else None
            cache.set(key, cached_data, timeout=60 * 60 * 24)

        return cached_data

    @staticmethod
    def get_default_city_group() -> "CityGroup":
        default_name = settings.DEFAULT_CITY_GROUP_NAME
        cg, created = CityGroup.objects.get_or_create(name=default_name)
        if created:
            cg.main_city = City.get_default_city()
            cg.save()

        return cg

    @staticmethod
    def get_default_city_group_pk() -> int:
        return CityGroup.get_default_city_group().pk


class CustomUser(AbstractUser):
    first_name = models.CharField(_("Имя"), max_length=35, blank=True, null=True)
    last_name = models.CharField(_("Фамилия "), max_length=35, blank=True, null=True)
    email = models.EmailField(
        _("Почта"),
        help_text=_("Адрес электронной почты"),
        unique=True,
        blank=True,
        null=True,
    )
    phone = models.CharField(
        verbose_name=_("Номер телефона"),
        null=True,
        blank=True,
        unique=True,
        max_length=16,
        help_text=_("В формате +7xxxxxxxxxx"),
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


class Store(TimeBasedModel):

    name = models.CharField(
        _("Название"),
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name=_("Город"),
        related_name="stores",
    )
    address = models.CharField(
        max_length=256,
        verbose_name="Адрес",
        null=True,
        blank=True,
    )
    phone = models.CharField(
        verbose_name=_("Номер телефона"),
        null=True,
        blank=True,
        unique=True,
        max_length=16,
        help_text=_("В формате +7xxxxxxxxxx"),
    )
    latitude = models.DecimalField(
        _("Широта"),
        max_digits=9,
        decimal_places=6,
    )
    longitude = models.DecimalField(
        _("Долгота"),
        max_digits=9,
        decimal_places=6,
    )
    

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")
        ordering = ("city", "-created_at")
        indexes = [
            models.Index(fields=["address"], name="store_address_idx"),
            models.Index(fields=["name"], name="store_name_idx"),
        ]

    def __str__(self) -> str:
        return f"Магазин {self.name}"


class Schedule(TimeBasedModel):

    schedule = models.CharField(_("График работы"), max_length=256)
    title = models.CharField(_("Заголовок"), max_length=128, blank=True, null=True)
    order = models.PositiveIntegerField(
        _("Порядковый номер"), default=0, blank=True, null=True
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        verbose_name=_("График работы"),
        related_name="schedules",
    )

    class Meta:
        verbose_name = _("График работы")
        verbose_name_plural = _("Графики работы")
        ordering = ("store", "-created_at")
        indexes = [
            models.Index(fields=["title"], name="schedule_title_idx"),
            models.Index(fields=["schedule"], name="schedule_schedule_idx"),
        ]

    def __str__(self) -> str:
        return f"#{self.id} График работы '{self.store.name}'"
