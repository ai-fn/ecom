import base64
import io
import os
from PIL import Image
from django.conf import settings
from loguru import logger
from shop.models import (
    ThumbModel,
)
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete


@receiver(pre_delete)
def delete_image_file(sender, instance, **kwargs):
    if issubclass(sender, ThumbModel):
        paths = []
        
        if hasattr(instance, "image") and instance.image:
            paths.append(instance.image.path)

        if hasattr(instance, "tiny_image") and instance.tiny_image:
            paths.append(instance.tiny_image.path)

        if hasattr(instance, "catalog_image") and instance.catalog_image:
            paths.append(instance.catalog_image.path)

            if hasattr(instance, "search_image") and instance.search_image:
                paths.append(instance.search_image.path)

        for path in paths:
            path = path.removeprefix("/code/")
            if path and os.path.isfile(path):
                os.remove(path)


@receiver(post_save)
def set_thumb(sender, instance, created, **kwargs):
    if not created:
        return

    if issubclass(sender, ThumbModel) and not instance.thumb_img:
        image_path = None
        if hasattr(instance, "image") and instance.image:
            image_path = instance.image.path
        elif hasattr(instance, "catalog_image") and instance.catalog_image:
            image_path = instance.catalog_image.path

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
                        instance.save()
            except Exception as err:
                logger.error(
                    f"Error while creating thumbnail image for {instance.__class__.__name__} object with pk {instance.pk}: {err}"
                )
