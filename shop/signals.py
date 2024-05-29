import base64
import io
import os
from PIL import Image
from django.conf import settings
from loguru import logger
from shop.models import (
    Category,
    Brand,
    CharacteristicValue,
    FooterItem,
    MainPageSliderImage,
    Page,
    Product,
    City,
    Characteristic,
    ThumbModel,
)
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, pre_delete
from django.utils.text import slugify as django_slugify
from unidecode import unidecode


slugify = lambda x: django_slugify(unidecode(x))


@receiver(pre_save)
def set_instance_order(sender, instance, **kwargs):
    if isinstance(sender, (Brand, Category, FooterItem, MainPageSliderImage)):
        if not instance.order:
            instance.order = get_order(sender)


@receiver(post_save, sender=City)
def set_domain(sender, created, instance, **kwargs):
    if created and not instance.domain:
        instance.domain = f'{slugify(instance.name)}.{getattr(settings, "BASE_DOMAIN", "krov.market")}'
        instance.save()


@receiver(post_save)
def set_instance_slug(sender, created, instance, **kwargs):
    if isinstance(sender, City):
        if created and not instance.domain:
            instance.domain = f'{slugify(instance.name)}.{getattr(settings, "BASE_DOMAIN", "krov.market")}'
            instance.save()
    elif isinstance(sender, Product):
        if created and not instance.slug:
            instance.slug = slugify(instance.title)
            instance.save()
    elif isinstance(sender, CharacteristicValue):
        if created and not instance.slug:
            instance.slug = slugify(instance.value)
            instance.save()

    elif isinstance(sender, (Category, Characteristic, Brand, Page)):
        if created and not instance.slug:
            instance.slug = slugify(instance.name) + f"-{instance.id}"
            instance.save()


def get_order(sender):
    last_obj = sender.objects.order_by("order").last()
    return last_obj.order + 1 if last_obj else 1


@receiver(pre_delete)
def delete_image_file(sender, instance, **kwargs):
    if issubclass(sender, ThumbModel):
        paths = []
        
        if hasattr(instance, "image") and instance.image:
            paths.append(instance.image.path)

        if hasattr(instance, "catalog_image") and instance.catalog_image:
            paths.append(instance.catalog_image.path)

            if hasattr(instance, "search_image") and instance.search_image:
                paths.append(instance.search_image.path)

        for path in paths:
            path = path.removeprefix("/code/")
            if path and os.path.isfile(path):
                os.remove(path)


@receiver(pre_save)
def set_thumb(sender, instance, **kwargs):
    if issubclass(sender, ThumbModel) and not instance.thumb_img:
        print("yappp")
        image_path = None
        if hasattr(instance, "image") and instance.image:
            image_path = instance.image.file.name
        elif hasattr(instance, "catalog_image") and instance.catalog_image:
            image_path = instance.catalog_image.file.name

        if image_path and os.path.isfile(image_path):
            try:
                with Image.open(image_path) as file:
                    thumb_image_size = (
                        getattr(settings, "THUMB_IMAGE_WIDTH", 10),
                        getattr(settings, "THUMB_IMAGE_HEIGHT", 10),
                    )
                    thumb_image = file.copy().resize(thumb_image_size)
                    with io.BytesIO() as buffer:
                        thumb_image.save(buffer, format="PNG")
                        instance.thumb_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
            except Exception as err:
                logger.error(
                    f"Error while creating thumbnail image for {instance.__class__.__name__} object with pk {instance.pk}: {err}"
                )
