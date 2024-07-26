import os
import uuid
import magic
import pandas as pd

from celery import shared_task

from django.db import transaction
from django.core.files.base import ContentFile

from loguru import logger

from tempfile import NamedTemporaryFile
from pytils import translit

from account.models import CityGroup
from shop.models import (
    Category,
    Characteristic,
    CharacteristicValue,
    Product,
    ProductImage,
    Price,
    City,
)

from import_app.models import ImportTask


@shared_task
def handle_xlsx_file_task(import_task_id: int, upload_type="PRODUCTS", path_to_images: str = "/tmp/import_images/"):
    try:
        import_task = ImportTask.objects.get(pk=import_task_id)
    except ImportTask.DoesNotExist:
        logger.info(f"ImportTask with provided pk '{import_task_id}' not found.")
        return False

    try:
        with open(import_task.file.path, "rb") as file_obj:
            # Проверка MIME-типа файла для удостоверения, что это действительно Excel файл
            mime_type = magic.from_buffer(file_obj.read(2048), mime=True)
            file_obj.seek(0)  # Возвращаем указатель в начало файла после чтения

            # Создание временного файла для хранения содержимого .xlsx файла
            with NamedTemporaryFile(suffix=".xlsx", delete=True) as tmp:
                tmp.write(file_obj.read())
                tmp.flush()
                tmp.seek(0)
                df = pd.read_excel(tmp.name, engine="openpyxl")
                # Вызов функции обработки DataFrame
                import_task.update_status("IN_PROGRESS")
                result = process_dataframe(df, upload_type, path_to_images)
                import_task.update_end_at()
                import_task.update_status("COMPLETED")
                return result
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        import_task.update_status("FAILED")
        return False


def process_dataframe(df, upload_type: str ="PRODUCTS", path_to_images: str = "/tmp/import_images/"):
    ignored_columns = [
        "TITLE",
        "DESCRIPTION",
        "IMAGES",
        "CATEGORIES",
        "SKU",
        "PRIORITY",
    ]
    failed_images = []
    city_names = City.objects.all().values_list("name", flat=True)
    try:
        with transaction.atomic():
            if upload_type == "PRODUCTS":

                characteristic_columns = []
                cities_columns = []

                for column_name in df.columns:
                    if column_name in city_names:
                        cities_columns.append(column_name)
                    elif column_name not in ignored_columns:
                        characteristic_columns.append(column_name)

                for _, row in df.iterrows():
                    category_path = row["CATEGORIES"].split(" | ")
                    category = None
                    for cat_name in category_path[
                        0:-1
                    ]:  # Правильное исключение последнего элемента
                        if (
                            cat_name
                        ):  # Дополнительная проверка на непустое имя категории
                            cat_slug = translit.slugify(cat_name)
                            if cat_slug:
                                parent_category = category
                                category, created = Category.objects.get_or_create(
                                    name=cat_name,
                                    defaults={
                                        "slug": cat_slug,
                                        "parent": parent_category,
                                    },
                                )
                                # Обновляем parent только если категория была только что создана или если parent отличается
                                if created or (
                                    category.parent != parent_category
                                    and parent_category is not None
                                ):
                                    category.parent = parent_category
                                    category.save()
                            else:
                                logger.error(
                                    f"Unable to create slug for category name '{cat_name}'. Skipping category creation."
                                )
                        else:
                            logger.error(
                                "Empty category name encountered. Skipping category creation."
                            )

                    product_title = row.get("TITLE")
                    product_slug = translit.slugify(product_title)
                    product_sku = row.get("SKU")  # Получаем артикул товара

                    if (
                        product_slug and product_sku
                    ):  # Проверяем, что slug продукта не пустой

                        product_priority = row.get("PRIORITY")
                        if (
                            product_priority
                            and isinstance(product_priority, (int, float))
                            and product_priority > 0
                        ):
                            product_priority = product_priority
                        else:
                            logger.info(
                                "Product PRIORITY not provided or invalid, use default"
                            )
                            product_priority = Product._meta.get_field(
                                "priority"
                            ).default

                        product_description = row.get(
                            "DESCRIPTION", "Описание отсутствует"
                        )

                        product, created = Product.objects.get_or_create(
                            article=product_sku,
                            defaults={
                                "title": product_title,
                                "priority": product_priority,
                                "description": product_description,
                                "category": category,
                                "slug": product_slug,
                            },
                        )

                        if not created:
                            product.slug = product_slug
                            product.title = product_title
                            product.description = product_description
                            product.priority = product_priority
                            product.save(
                                update_fields=["description", "priority", "title"]
                            )

                        product_image_urls = row["IMAGES"].split(",")
                        if len(product_image_urls) > 0:
                            for idx, image_url in enumerate(product_image_urls):

                                image_path = os.path.join(path_to_images, image_url)
                                if not os.path.isfile(image_url):
                                    logger.info(f"No such file or directory: {image_path}. Continue...")
                                    continue

                                with open(image_url, "rb") as image_file:
                                    image_data = image_file.read()

                                try:
                                    format = "webp"
                                    filename = f"image-{uuid.uuid4()}"

                                    # Сохранение первого изображение в нескольких форматах
                                    if idx == 0:

                                        images_types = ["catalog", "search", "original"]
                                        for img_type in images_types:
                                            attr_name = img_type + "_image"
                                            attr = getattr(product, attr_name, None)
                                            if not attr:
                                                continue
                                            attr.save(
                                                f"{img_type}-{filename}.{format}",
                                                ContentFile(image_data),
                                                save=False,
                                            )

                                        product.catalog_image.save(
                                            f"catalog-{filename}.{format}",
                                            ContentFile(image_data),
                                            save=False,
                                        )
                                        product.search_image.save(
                                            f"search-{filename}.{format}",
                                            ContentFile(image_data),
                                            save=False,
                                        )

                                        product.save(
                                            update_fields=[
                                                "search_image",
                                                "catalog_image",
                                                "original_image",
                                            ]
                                        )

                                    product_image = ProductImage(product=product)
                                    product_image.image.save(
                                        filename + f".{format}",
                                        ContentFile(image_data),
                                    )
                                    print(f"{product_image} saved")

                                except Exception as err:
                                    failed_images.append(image_url)
                                    print(f"Error while save ProductImage: {err}")

                        # Обработка цен по городам
                        if cities_columns:
                            for column_name in cities_columns:
                                try:
                                    city_group = CityGroup.objects.get(name=column_name)
                                except CityGroup.DoesNotExist:
                                    logger.info(f"CityGroup with name '{column_name}' does not exists. Continue...")
                                    continue

                                new_price = float(row[column_name])
                                price, created = Price.objects.get_or_create(
                                    product=product,
                                    city_group=city_group,
                                    defaults={"price": new_price},
                                )

                                if not created:
                                    price.old_price = price.price
                                    price.price = new_price
                                    price.save()

                        # Обработка характеристик и их значений
                        if characteristic_columns:
                            for column_name in characteristic_columns:

                                characteristic_value = row[column_name]
                                if pd.notna(
                                    characteristic_value
                                ):  # Проверка наличия значения
                                    # Проверка существования характеристики и создание, если не существует
                                    characteristic, _ = (
                                        Characteristic.objects.get_or_create(
                                            slug=translit.slugify(column_name),
                                            defaults={"category": category, "name": column_name},
                                        )
                                    )
                                    # Создание значения характеристики для продукта
                                    val, created = (
                                        CharacteristicValue.objects.get_or_create(
                                            product=product,
                                            characteristic=characteristic,
                                            defaults={
                                                "value": str(characteristic_value)
                                            },
                                        )
                                    )
                                    if not created:
                                        val.value = characteristic_value
                                        val.save(update_fields=["value"])

                    else:
                        logger.error(
                            f"Unable to create product with title '{product_title}' and article '{product_sku}'. Skipping product creation."
                        )
        return failed_images or []
    except Exception as err:
        print(f"Error processing data: {err}")
