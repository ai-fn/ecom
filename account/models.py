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
    name = models.CharField(max_length=255, verbose_name="Город")
    domain = models.CharField(max_length=255, verbose_name="Домен")

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    phone = models.CharField(verbose_name="Номер телефона", max_length=16, null=True)
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, related_name="customers"
    )
