import base64
import io
import os
from PIL import Image
from django.conf import settings
from loguru import logger
from shop.models import ThumbModel
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.db.models.signals import post_save, pre_delete


@receiver(pre_delete)
def delete_image_file(sender, instance, **kwargs):
    """
    Удаляет связанные файлы изображений при удалении объекта.

    :param sender: Отправитель сигнала.
    :param instance: Экземпляр удаляемой модели.
    :param kwargs: Дополнительные параметры.
    """
    if issubclass(sender, ThumbModel):

        image_fields = ("image", "tiny_image", "catalog_image", "search_image")
        for field_name in image_fields:

            if hasattr(instance, field_name) and (val := getattr(instance, field_name)):
                if (del_func := getattr(val, "delete", None)) and callable(del_func):
                    del_func()


@receiver(post_save)
def set_thumb(sender, instance, created, **kwargs):
    """
    Создает уменьшенное изображение (thumbnail) после создания объекта.

    :param sender: Отправитель сигнала.
    :param instance: Экземпляр созданной модели.
    :param created: Флаг, указывающий, был ли объект только что создан.
    :param kwargs: Дополнительные параметры.
    """
    if not created:
        return

    thumb_image_size = (
        getattr(settings, "THUMB_IMAGE_WIDTH", 10),
        getattr(settings, "THUMB_IMAGE_HEIGHT", 10),
    )

    if issubclass(sender, ThumbModel) and not instance.thumb_img:
        image_path = None

        # Определяем путь к исходному изображению
        if hasattr(instance, "image") and instance.image:
            image_path = instance.image.url
        elif hasattr(instance, "catalog_image") and instance.catalog_image:
            image_path = instance.catalog_image.url

        # Генерация уменьшенного изображения
        if image_path:
            try:
                with default_storage.open(image_path) as image_file:
                    with io.BytesIO(image_file.read()) as file_buffer:
                        with Image.open(file_buffer) as image_obj:
                            thumb_image = image_obj.resize(thumb_image_size)

                with io.BytesIO() as buffer:
                    thumb_image.save(buffer, format="PNG")
                    # Кодирование в Base64
                    instance.thumb_img = base64.b64encode(buffer.getvalue()).decode(
                        "utf-8"
                    )
                    instance.save()
            except FileNotFoundError as f_err:
                logger.info(f"FileNotFound on creating thumb for {instance.__class__.__name__} object with pk {instance.pk}: {f_err}")
            except Exception as err:
                logger.error(
                    f"Error while creating thumbnail image for {instance.__class__.__name__} object with pk {instance.pk}: {err}"
                )
