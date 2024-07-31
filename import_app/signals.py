from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.utils.text import slugify as django_slugify
from unidecode import unidecode

from import_app.models import ImportSetting


@receiver(pre_save)
def set_slug(sender, instance, **kwargs):
    if isinstance(instance, ImportSetting) and instance.name and not instance.slug:
        instance.slug = django_slugify(unidecode(instance.name))
